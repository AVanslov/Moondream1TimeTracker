# Трекер для замера времения генерации описания фотографий в модели Moondream1

## Данные компьютера
Запуск модели произведен на локальном компьютере Lenovo IdeaPad Slim 3 15ABR8 под операционной системой Linux Ubuntu 22.04.5 LTS 64-bit

| Parameter                     | Value                                                                 |
| ----------------------------- | --------------------------------------------------------------------- |
| **Processor**                  | AMD® Ryzen 5 7530U with Radeon Graphics × 12                         |
| **Architecture**               | x86_64                                                              |
| **CPU(s)**                     | 12 (12 threads total)                                                |
| **Core(s) per socket**         | 6 (6 physical cores)                                                 |
| **Thread(s) per core**         | 2 (Hyper-Threading technology)                                       |
| **CPU max MHz**                | 4546.0000 MHz (4.5 GHz)                                              |
| **CPU min MHz**                | 400.0000 MHz (0.4 GHz, power saving mode)                            |
| **L1d Cache**                  | 192 KiB                                                              |
| **L1i Cache**                  | 192 KiB                                                              |
| **L2 Cache**                   | 3 MiB                                                                |
| **L3 Cache**                   | 16 MiB                                                               |
| **Virtualization**             | AMD-V                                                               |
| **CPU Flags**                  | avx, avx2, sse4_1, sse4_2, fma                                      |
| **NUMA**                       | NUMA node(s): 1                                                      |
| **Memory**                     | 16.0 GiB                                                            |
| **Memory Type**                | DDR4                                                                |
| **Memory Speed**               | 3200 MT/s                                                            |
| **Graphics**                   | RENOIR (LLVM 15.0.7, DRM 3.57, 6.8.0-49-generic)                     |
| **VGA Controller**             | Advanced Micro Devices, Inc. [AMD/ATI] Barcelo (rev c5)              |
| **OpenGL Renderer**            | RENOIR (LLVM 15.0.7, DRM 3.57, 6.8.0-49-generic)                     |
| **Number of Platforms**        | 0 FLOPS                                                              |
| **Disk Type**                  | SSD                                                                  |
| **Disk Model**                 | SAMSUNG MZAL41T0HBLB-00BL2                                            |
| **IOPS (Cached Reads)**        | 41406 MB in 1.97 seconds = 21021.80 MB/sec                          |
| **IOPS (Buffered Reads)**      | 2428 MB in 3.00 seconds = 809.00 MB/sec                             |
| **Operating System**           | Linux han-solo 6.8.0-49-generic #49~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC |
| **Kernel**                     | 6.8.0-49-generic #49~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC             |


## Общие данные

### Тесты
**При тестах локально в режиме balanced (средняя производительность локального компьютера):**

Task Execution Statistics:
Minimum Time: 5.90 seconds
Average Time: 13.58 seconds
Maximum Time: 68.50 seconds

**При тестах локально в режиме perfomance (средняя производительность локального компьютера):**

Task Execution Statistics:
Minimum Time: 5.87 seconds
Average Time: 13.13 seconds
Maximum Time: 73.63 seconds

**При тестах локально в режиме perfomance и текст задания разделен запятыми(средняя производительность локального компьютера):**

Task Execution Statistics:
Minimum Time: 5.31 seconds
Average Time: 13.08 seconds
Maximum Time: 70.21 seconds

В [данной google таблице](https://docs.google.com/spreadsheets/d/1XljgI5tSydZUFfA2oEotvUn_NAvlK6QawdEpxxxvkCE/edit?usp=sharing) на листах LocalTestsBalaced и LocalTestsPerfomance или в файлах csv [perfomance mode](/perfomance_mode_metrics.csv), [balanced mode](/balance_mode_metrics.csv) вы найдете подробный отчет о локальных тестах.

## Рассчет времени выполнения полного датасета на сервере

В файле [./ServerCalculator.py](ServerCalculator.py) написан скрипт, которые на основе данных локального компьютера, на котором тестируется часть датасета, на основе данных сервера и на средней скорости обработки одного изображения локально расчитывается время обработки всего датасета на сервере.

### System Specifications Used in Script

| Parameter       | Value                                      | Constant Name        |
| --------------- | ------------------------------------------ | -------------------- |
| **CPU(s)**      | 12 (12 threads total)                      | `LOCAL_CPU_CORES`    |
| **IOPS (Cached Reads)** | 41406 MB in 1.97 seconds = 21021.80 MB/sec | `LOCAL_IOPS`         |
| **IOPS (Buffered Reads)** | 2428 MB in 3.00 seconds = 809.00 MB/sec  | `LOCAL_IOPS`         |
| **FLOPS**        | 4.5 TFLOPS (примерная производительность процессора)  | `LOCAL_FLOPS`        |


Для работы скрипта нужно зайти на сервер и выполнить в нем команды для получения данных о максимальной производительности процессора, числе ядер процессора, скорости ввода-вывода за секунду, данные оперативной памяти.

**Например, так:**

### lscpu:

```
bash
Copy code
CPU(s):              16
Thread(s) per core:  2
Core(s) per socket:  8
CPU max MHz:         3500.00
CPU min MHz:         800.00
```

### iostat -dx 1:

```
bash
Copy code
Device            r/s     w/s     rkB/s   wkB/s   await  svctm  %util
sda              20.0    15.0    1200    800     10.0   1.5    5.0
```

### free -h:

```
bash
Copy code
total        used        free      shared  buff/cache   available
Mem:          16Gi        4Gi        8Gi       0.5Gi      4Gi         10Gi
```

## Пример расчета времени обработки всего датасета на сервере
Например, оценочное время обработки датасета из 230 000 фотографий на сервере со следующими данными

#### Server Specifications Used in Script

| Parameter       | Value                                      | Constant Name        |
| --------------- | ------------------------------------------ | -------------------- |
| **FLOPS**        | 10 TFLOPS (примерная производительность процессора) | `SERVER_FLOPS`       |
| **CPU(s)**       | 32 (32 threads total)                      | `SERVER_CPU_CORES`   |
| **IOPS**         | 1500.00 IOPS                               | `SERVER_IOPS`        |

И если основываться на данных локального теста в режиме balanced - средняя производительность, где среднее время обработки одной фотографии - 13.58 секунд

**Заняло бы: 78.96 часов**

То же самое, но если проводить локальный тест в режиме perfomence - максимальная производитенльность, где среднее время обработки одной фотографии - 13.13 секунд

**Заняло бы: 76.35 часов**

**Заняло бы, если текст задания разделен запятыми: 76.06 часов**
