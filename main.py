import csv
import os
import time

import moondream as md
from PIL import Image

#  Configurations
IMAGE_FOLDER = './images'  # Путь к папке с фотографиями
TASK_DESCRIPTION = (
    'Tell me Context of an outfit'
    'Tell me Theme of an outfit'
    'Tell me Collection Notes of an outfit'
    'Tell me Garment of an outfit'
    'Tell me Garment style of an outfit'
    'Tell me Design elements of an outfit'
    'Tell me vibe of an outfit'
    'Tell me emotional tone of an outfit'
)  # Описание задачи
OUTPUT_CSV = 'perfomance_mode_metrics.csv'  # Имя выходного CSV файла

# Initialize Model
MODEL_PATH = './moondream-0_5b-int8.mf.gz'
model = md.vl(model=MODEL_PATH)  # Загрузка модели

# Prepare CSV File
with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Image', 'Task', 'Result', 'Execution Time (seconds)'])

# Process Images
execution_times = []

for image_name in os.listdir(IMAGE_FOLDER):
    image_path = os.path.join(IMAGE_FOLDER, image_name)

    if not os.path.isfile(image_path):
        continue  # Пропустить, если это не файл

    try:
        # Загружаем изображение
        image = Image.open(image_path)
        encoded_image = model.encode_image(image)  # Кодируем изображение

        # Замеряем время выполнения задачи
        start_time = time.time()
        result = model.caption(encoded_image)['caption']  # Выполнение задачи
        end_time = time.time()

        execution_time = end_time - start_time
        execution_times.append(execution_time)

        # Сохраняем результат в CSV
        with open(OUTPUT_CSV, mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([image_name, TASK_DESCRIPTION, result, execution_time])

        print(f'Processed {image_name}: {result} (Time: {execution_time:.2f} seconds)')

    except Exception as e:
        print(f'Error processing {image_name}: {e}')

# Calculate and Display Statistics
if execution_times:
    min_time = min(execution_times)
    max_time = max(execution_times)
    avg_time = sum(execution_times) / len(execution_times)

    print('\nTask Execution Statistics:')
    print(f'Minimum Time: {min_time:.2f} seconds')
    print(f'Average Time: {avg_time:.2f} seconds')
    print(f'Maximum Time: {max_time:.2f} seconds')
else:
    print('No valid images processed.')
