"""
Используйте
celery -A tasks worker --loglevel=info --concurrency=N, где N = колличество ядер / 2
Чтобы не перенагружать систему
"""
import csv
import os
import time
from PIL import Image
from celery import Celery
from constants import IMAGE_FOLDER, TASK_DESCRIPTION, OUTPUT_CSV, BATCH_SIZE, MODEL_PATH
import moondream as md
from multiprocessing import Lock
import fcntl

# Настройка Celery
app = Celery('image_processing', broker='redis://localhost:6379/0')

# Настройка времени таймаута для задач Celery
app.conf.task_time_limit = 600  # Максимальное время на выполнение задачи (10 минут)
app.conf.task_soft_time_limit = 300  # Мягкий таймаут для выполнения задачи (5 минут)

model = md.vl(model=MODEL_PATH)  # Загрузка модели

# Глобальная блокировка для защиты записи в CSV
lock = Lock()


def resize_image(image, max_width=800, max_height=600):
    """Функция для уменьшения изображения до заданных размеров."""
    width, height = image.size

    # Определяем пропорции, чтобы сохранить соотношение сторон
    ratio = min(max_width / width, max_height / height)

    if ratio < 1:  # Если картинка больше, чем максимальные размеры, уменьшаем
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return image


def is_image_processed(image_path):
    """Проверяет, было ли изображение уже обработано."""
    if not os.path.isfile(OUTPUT_CSV):
        return False

    with open(OUTPUT_CSV, mode='r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        return any(row[0] == image_path for row in reader)


def normalize_row(row):
    """Удаляет пробелы и нормализует строку для проверки уникальности."""
    return tuple(str(item).strip() for item in row)


def write_to_csv(rows, header=None):
    """Функция для пакетной записи в CSV с блокировкой."""
    with lock:
        file_exists = os.path.isfile(OUTPUT_CSV)

        # Загружаем уже существующие данные
        existing_rows = set()
        if file_exists:
            with open(OUTPUT_CSV, mode='r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                next(reader, None)  # Пропускаем заголовок
                existing_rows = {normalize_row(row) for row in reader}

        # Добавляем только новые строки
        new_rows = [row for row in rows if normalize_row(row) not in existing_rows]

        if not new_rows:
            return  # Нечего добавлять

        with open(OUTPUT_CSV, mode='a', newline='', encoding='utf-8') as csv_file:
            fcntl.flock(csv_file, fcntl.LOCK_EX)  # Устанавливаем блокировку файла

            writer = csv.writer(csv_file)

            # Если файл только создается, добавляем заголовки
            if not file_exists and header:
                writer.writerow(header)

            writer.writerows(new_rows)

            fcntl.flock(csv_file, fcntl.LOCK_UN)  # Снимаем блокировку файла


@app.task(bind=True, max_retries=3, default_retry_delay=60, time_limit=600, soft_time_limit=300)
def process_image(self, image_path):
    """Обработка одного изображения с таймаутом."""
    try:
        if is_image_processed(image_path):
            print(f"Image {image_path} is already processed. Skipping.")
            return

        start_time = time.time()
        image = Image.open(image_path)
        print(f"Image loading time: {time.time() - start_time:.2f} seconds")

        start_time = time.time()
        image = resize_image(image)
        print(f"Image resizing time: {time.time() - start_time:.2f} seconds")

        start_time = time.time()
        encoded_image = model.encode_image(image)
        print(f"Image encoding time: {time.time() - start_time:.2f} seconds")

        start_time = time.time()
        full_caption = model.caption(encoded_image)['caption']
        print(f"Caption generation time: {time.time() - start_time:.2f} seconds")

        # Если это строка, возвращаем её для всех задач
        results = {task: full_caption for task in TASK_DESCRIPTION}

        end_time = time.time()
        execution_time = end_time - start_time

        # Формируем строку для записи
        row = [image_path, *results.values(), execution_time]

        # Пишем в CSV
        header = ['Image Path'] + TASK_DESCRIPTION + ['Execution Time']
        write_to_csv([row], header=header)

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        raise self.retry(exc=e)  # Повтор задачи при ошибке


@app.task
def process_batch(image_batch):
    """Обработка пакета изображений"""
    # Удаляем дубликаты путей в текущем пакете
    unique_image_batch = list(set(image_batch))

    rows_to_write = []

    for image_path in unique_image_batch:
        start_time = time.time()
        process_image(image_path=image_path)
        print(f"Image batch processing time: {time.time() - start_time:.2f} seconds")


@app.task
def start_processing():
    """Запуск пакетной обработки изображений"""
    # Получение всех путей к изображениям
    image_paths = list(set(
        os.path.join(IMAGE_FOLDER, image_name)
        for image_name in os.listdir(IMAGE_FOLDER)
        if os.path.isfile(os.path.join(IMAGE_FOLDER, image_name))
    ))

    image_batches = [image_paths[i:i + BATCH_SIZE] for i in range(0, len(image_paths), BATCH_SIZE)]  # Разделяем на пакеты

    for image_batch in image_batches:
        process_batch.apply_async(args=[image_batch])
