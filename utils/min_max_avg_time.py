import csv

# Путь к вашему CSV файлу
INPUT_CSV = './metrics/metrics.csv'


def calculate_execution_times(csv_file):
    execution_times = []

    # Чтение CSV файла
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Чтение значения времени выполнения из строки
                execution_time = float(row['Execution Time'])
                execution_times.append(execution_time)
            except ValueError:
                # Пропуск строки, если значение времени выполнения не является числом
                continue

    # Если список с временами не пустой, вычисляем статистику
    if execution_times:
        min_time = min(execution_times)
        max_time = max(execution_times)
        avg_time = sum(execution_times) / len(execution_times)

        return min_time, avg_time, max_time
    else:
        return None, None, None

# Вычисление статистики
min_time, avg_time, max_time = calculate_execution_times(INPUT_CSV)

# Вывод результатов
if min_time is not None:
    print(f'Minimum Time: {min_time:.2f} seconds')
    print(f'Average Time: {avg_time:.2f} seconds')
    print(f'Maximum Time: {max_time:.2f} seconds')
else:
    print('No valid execution times found in the CSV file.')
