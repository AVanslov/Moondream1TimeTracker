import os
import time
import csv

# Константы характеристик системы
LOCAL_FLOPS = 4.5 * 10**12       # 4.5 TFLOPS
LOCAL_CPU_CORES = 12            # 12 потоков
LOCAL_IOPS = 809.00             # IOPS диска локальной машины

SERVER_FLOPS = 10 * 10**12      # 10 TFLOPS
SERVER_CPU_CORES = 32          # 32 потока
SERVER_IOPS = 1500.00          # IOPS сервера

LOCAL_DATASET_SIZE = 45       # Количество изображений в локальном датасете
FULL_DATASET_SIZE = 230000      # Количество изображений в полном датасете

LOCAL_PER_IMAGE_TIME = 13.08       # Среднее время обработки одного изображения локально (в секундах)


def calculate_server_time(local_per_image_time, local_specs, server_specs, local_dataset_size, full_dataset_size):
    """
    Рассчитать предполагаемое время обработки датасета на сервере, основываясь на характеристиках локальной системы и сервера.

    Параметры:
        local_per_image_time (float): Среднее время обработки одного изображения на локальной машине (в секундах).
        local_specs (dict): Характеристики локальной системы.
        server_specs (dict): Характеристики сервера.
        local_dataset_size (int): Количество изображений в локальном датасете.
        full_dataset_size (int): Количество изображений в полном датасете.

    Возвращает:
        float: Оценочное время обработки полного датасета на сервере (в секундах).
    """
    # Рассчитать относительную производительность на основе FLOPS, ядер CPU и IOPS диска
    performance_ratio = (
        (server_specs['flops'] / local_specs['flops']) *
        (server_specs['cpu_cores'] / local_specs['cpu_cores']) *
        (server_specs['iops'] / local_specs['iops'])
    )

    # Оценить время обработки полного датасета на сервере
    estimated_server_time = (local_per_image_time / performance_ratio) * full_dataset_size

    return estimated_server_time

# ===== Пример использования =====
if __name__ == "__main__":
    # Характеристики локальной системы
    local_specs = {
        'flops': LOCAL_FLOPS,
        'cpu_cores': LOCAL_CPU_CORES,
        'iops': LOCAL_IOPS
    }

    # Характеристики сервера
    server_specs = {
        'flops': SERVER_FLOPS,
        'cpu_cores': SERVER_CPU_CORES,
        'iops': SERVER_IOPS
    }

    # Рассчитать время обработки на сервере
    estimated_server_time = calculate_server_time(
        LOCAL_PER_IMAGE_TIME, local_specs, server_specs, LOCAL_DATASET_SIZE, FULL_DATASET_SIZE
    )

    print(f"Оценочное время обработки полного датасета на сервере: {estimated_server_time / 3600:.2f} часов")
