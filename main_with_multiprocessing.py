"""
Minimum Time: 7.98 seconds
Average Time: 18.97 seconds
Maximum Time: 27.52 seconds
"""
import csv
import os
import time
from multiprocessing import Pool
import moondream as md
from PIL import Image

# Configurations
IMAGE_FOLDER = './images'
TASK_DESCRIPTION = (
    'Tell me Context of an outfit, '
    'Tell me Theme of an outfit, '
    'Tell me Collection Notes of an outfit, '
    'Tell me Garment of an outfit, '
    'Tell me Garment style of an outfit, '
    'Tell me Design elements of an outfit, '
    'Tell me vibe of an outfit, '
    'Tell me emotional tone of an outfit.'
)
OUTPUT_CSV = 'task_with_commas_metrics.csv'
MODEL_PATH = './moondream-0_5b-int8.mf.gz'
TASK_TIMEOUT = 60  # Таймаут для каждой задачи в секундах

# Load the model once in the main process
model = md.vl(model=MODEL_PATH)


# Function to process a single image
def process_image(image_name):
    try:
        image_path = os.path.join(IMAGE_FOLDER, image_name)
        if not os.path.isfile(image_path):
            return None  # Skip non-files

        # Load and resize image while maintaining aspect ratio
        image = Image.open(image_path)
        original_width, original_height = image.size

        # Calculate scaling factor to maintain aspect ratio
        scaling_factor = 512 / max(original_width, original_height)
        new_width = int(original_width * scaling_factor)
        new_height = int(original_height * scaling_factor)

        # Resize the image
        image = image.resize((new_width, new_height), Image.LANCZOS)
        encoded_image = model.encode_image(image)

        # Perform task and measure execution time
        start_time = time.time()
        result = model.caption(encoded_image)['caption']
        execution_time = time.time() - start_time

        print(f'Processed {image_name}: {result[:100]} (Time: {execution_time:.2f} seconds)')
        return [image_name, TASK_DESCRIPTION, result, execution_time]
    except Exception as e:
        print(f'Error processing {image_name}: {e}')
        return [image_name, TASK_DESCRIPTION, f"Error: {e}", 0]


# Main function to handle multiprocessing pool
def main():
    # Prepare CSV file
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Image', 'Task', 'Result', 'Execution Time (seconds)'])

    # Get list of images
    image_names = os.listdir(IMAGE_FOLDER)

    # Use multiprocessing pool with a fixed number of processes (2)
    with Pool(processes=2) as pool:
        results = pool.map(process_image, image_names)

    # Write results to CSV
    with open(OUTPUT_CSV, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(filter(None, results))


if __name__ == '__main__':
    main()
