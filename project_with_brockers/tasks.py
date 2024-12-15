import csv
import os
import time
import cv2  # OpenCV для обработки изображений
from celery import Celery
from constants import IMAGE_FOLDER, TASK_DESCRIPTION, OUTPUT_CSV, BATCH_SIZE, MODEL_PATH
import moondream as md
from multiprocessing import Lock
import fcntl
from PIL import Image

# Настройка Celery
app = Celery('image_processing', broker='redis://localhost:6379/0')

# Настройка времени таймаута для задач Celery
app.conf.task_time_limit = 600
app.conf.task_soft_time_limit = 300

model = md.vl(model=MODEL_PATH)  # Загрузка модели

# Глобальная блокировка для защиты записи в CSV
lock = Lock()

current_csv_index = 0  # Индекс текущего CSV-файла


def get_csv_file():
    """Получить имя текущего CSV-файла, создавая новый при необходимости."""
    global current_csv_index

    current_file = f"{OUTPUT_CSV}_{current_csv_index}.csv"
    
    if not os.path.isfile(current_file):
        return current_file

    # Проверяем количество строк в текущем файле
    with open(current_file, mode='r', encoding='utf-8') as csv_file:
        line_count = sum(1 for _ in csv_file)

    # Если превышено 50,000 строк, переключаемся на новый файл
    if line_count >= 50000:
        current_csv_index += 1
        return f"{OUTPUT_CSV}_{current_csv_index}.csv"

    return current_file


def resize_image_opencv(image_path, max_width=256, max_height=256):
    """Функция для уменьшения изображения с использованием OpenCV."""
    img = cv2.imread(image_path)  # Чтение изображения
    if img is None:
        raise ValueError(f"Image {image_path} could not be loaded.")

    h, w = img.shape[:2]
    scale = min(max_width / w, max_height / h)

    if scale < 1:
        new_size = (int(w * scale), int(h * scale))
        img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

    return img


def is_image_processed(image_path):
    """Проверяет, было ли изображение уже обработано."""
    current_file = get_csv_file()
    if not os.path.isfile(current_file):
        return False

    with open(current_file, mode='r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        return any(row[0] == image_path for row in reader)


def write_to_csv(rows, header=None):
    """Функция для пакетной записи в CSV с блокировкой."""
    with lock:
        current_file = get_csv_file()
        file_exists = os.path.isfile(current_file)

        # Добавляем строки в файл
        with open(current_file, mode='a', newline='', encoding='utf-8') as csv_file:
            fcntl.flock(csv_file, fcntl.LOCK_EX)
            writer = csv.writer(csv_file)
            if not file_exists and header:
                writer.writerow(header)
            writer.writerows(rows)
            fcntl.flock(csv_file, fcntl.LOCK_UN)


@app.task(bind=True, max_retries=3, default_retry_delay=60, time_limit=600, soft_time_limit=300)
def process_image(self, image_path):
    """Обработка одного изображения с использованием OpenCV."""
    try:
        if is_image_processed(image_path):
            print(f"Image {image_path} is already processed. Skipping.")
            return

        start_time = time.time()
        img = resize_image_opencv(image_path)
        print(f"Image resizing time: {time.time() - start_time:.2f} seconds")

        # Преобразуем изображение в формат Pillow
        pillow_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        start_time = time.time()
        encoded_image = model.encode_image(pillow_image)  # Передаём Pillow изображение
        print(f"Image encoding time: {time.time() - start_time:.2f} seconds")

        start_time = time.time()
        full_caption = model.caption(encoded_image)['caption']
        print(f"Caption generation time: {time.time() - start_time:.2f} seconds")

        results = {task: full_caption for task in TASK_DESCRIPTION}
        execution_time = time.time() - start_time

        row = [image_path, *results.values(), execution_time]
        header = ['Image Path'] + TASK_DESCRIPTION + ['Execution Time']
        write_to_csv([row], header=header)

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        raise self.retry(exc=e)


@app.task
def process_batch(image_batch):
    """Обработка пакета изображений."""
    for image_path in set(image_batch):
        process_image.apply_async(args=[image_path])


@app.task
def start_processing():
    """Запуск пакетной обработки изображений."""
    image_paths = [
        os.path.join(IMAGE_FOLDER, name)
        for name in os.listdir(IMAGE_FOLDER)
        if os.path.isfile(os.path.join(IMAGE_FOLDER, name))
    ]
    batches = [image_paths[i:i + BATCH_SIZE] for i in range(0, len(image_paths), BATCH_SIZE)]

    for batch in batches:
        process_batch.apply_async(args=[batch])
