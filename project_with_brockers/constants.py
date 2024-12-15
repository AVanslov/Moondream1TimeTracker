# Константы

# Путь к папке с изображениями
IMAGE_FOLDER = '../images'

# Описание задач
TASK_DESCRIPTION = [
    'Tell me about the outfit'
]

# Путь к модели
MODEL_PATH = '../moondream-0_5b-int8.mf.gz'

# Выходной CSV файл
OUTPUT_CSV = '../metrics/metrics.csv'

# Размер пакета изображений
BATCH_SIZE = 4  # Размер пакета изображений для обработки

# Тайм-ауты
IMAGE_PROCESSING_TIMEOUT = 60  # Тайм-аут для обработки одного изображения
BATCH_PROCESSING_TIMEOUT = 120  # Тайм-аут для обработки пакета
