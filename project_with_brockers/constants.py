# Константы

# Путь к папке с изображениями
IMAGE_FOLDER = '../images'

# Описание задач
TASK_DESCRIPTION = [
    # 'Tell me Context of an outfit',
    # 'Tell me Theme of an outfit',
    # 'Tell me Collection Notes of an outfit',
    # 'Tell me Garment of an outfit',
    # 'Tell me Garment style of an outfit',
    # 'Tell me Design elements of an outfit',
    # 'Tell me vibe of an outfit',
    # 'Tell me emotional tone of an outfit',
    'Tell me about the outfit'
]

# Путь к модели
MODEL_PATH = '../moondream-0_5b-int8.mf.gz'

# Выходной CSV файл
OUTPUT_CSV = 'with_brockers_metrics.csv'

# Максимальный размер изображения
MAX_IMAGE_SIZE = 1024  # Максимальный размер изображения

# Размер пакета изображений
BATCH_SIZE = 4  # Размер пакета изображений для обработки

# Тайм-ауты
IMAGE_PROCESSING_TIMEOUT = 60  # Тайм-аут для обработки одного изображения
BATCH_PROCESSING_TIMEOUT = 120  # Тайм-аут для обработки пакета
