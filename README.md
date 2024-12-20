# Documentation for the Image Processing Module Using the Moondream1 Model

## Overview

This module is designed to process images using the Moondream1 model and return specific information about them. It executes tasks based on text commands provided in the `TASK_DESCRIPTION` constant in the `constants.py` file. You can specify a list of commands, not just a single one, allowing flexibility in how the images are analyzed or described.

### Key Features:
- **Task Customization:** Define specific tasks or questions for image analysis by setting the `TASK_DESCRIPTION` constant.
- **Message Broker Support:** The module uses message brokers for efficient parallel task execution.
- **Performance Utilities:** Includes utilities for performance analysis:
  - **`min_max_avg_time.py`:** Calculates the minimum, maximum, and average processing times based on CSV output.
  - **`ServerCalculator.py`:** Estimates server-side processing speed based on local dataset metrics and server specifications.
- **Makefile Automation:** A `Makefile` is included to automate setup, downloading the model, and running the module on an Ubuntu server.

---

## Installation and Deployment

### 1. Using the Makefile

For Ubuntu servers, you can use the provided `Makefile` to automate the installation and deployment process:

1. **Install Required Dependencies:**
   ```bash
   make setup
   ```
2. **Download and Extract the Model:**
   ```bash
   make model
   ```
3. **Start Redis Server:**
   ```bash
   make redis
   ```
4. **Run the Module:**
   ```bash
   make run
   ```

### 2. Manual Setup

If you prefer not to use the `Makefile`, follow these steps. These instructions mirror the `Makefile` commands for consistency:

1. **Install Required Dependencies:**
   ```bash
   apt-get update && apt-get install -y redis-server
   pip3 install -r requirements.txt
   ```
2. **Download and Extract the Model:**
   ```bash
   wget https://download.moondream.ai/models/moondream-0_5b-int8.mf.gz
   mkdir -p model
   gzip -d -c moondream-0_5b-int8.mf.gz > model/moondream-0_5b-int8.model
   ```
3. **Start Redis Server:**
   ```bash
   systemctl start redis
   ```
4. **Run Celery Workers:**
   ```bash
   celery -A tasks worker --loglevel=info --concurrency=16
   ```
5. **Run the Script:**
   ```bash
   python run.py
   ```

---

## System Requirements

### Minimum Server Specifications:
- **Processor:** CPU with at least 32 cores (to support 16 workers effectively).
- **FLOPS:** 10 TFLOPS (Floating Point Operations per Second).
- **IOPS:** 1500 IOPS (Input/Output Operations per Second).
- **Memory:** At least 64 GB RAM.
- **Disk:** High-speed SSD.

---

## Preparing Your Dataset

Before starting the module, place the images you want to process in the `images` directory in the project root. The module will automatically process all images in this directory.

---

## Performance Estimation

### Estimating Processing Time on a Server

Use the `ServerCalculator.py` script to estimate the time required to process a dataset on a server.

1. **Run the Script:**
   ```bash
   python ServerCalculator.py
   ```
2. **Inputs:**
   - Local machine specifications (CPU, FLOPS, IOPS).
   - Average processing time per image locally.
   - Server specifications.
   - Dataset size.
3. **Output:**
   The script will provide an estimated time in hours to process the dataset on the server.

### Example:
- **Local Machine:**
  - 12 cores, 4.5 TFLOPS, 809 IOPS.
  - Average time per image: 25.56 seconds.
- **Server Specifications:**
  - 32 cores, 10 TFLOPS, 1500 IOPS.

Estimated processing time for 230,000 images: ~9.29 hours.

---

## Additional Utilities

### 1. `min_max_avg_time.py`
Analyze the performance of image processing tasks based on CSV logs:

- **Input:** CSV file generated by the module.
- **Output:** Minimum, maximum, and average processing times.

### Usage:
```bash
python min_max_avg_time.py --csv-file <path_to_csv>
```

---

## Configurations

### Constants in `constants.py`
- **`TASK_DESCRIPTION`:** Define the tasks or questions the module should process.
  Example:
  ```python
  TASK_DESCRIPTION = ["Describe the outfit", "What is the primary color?"]
  ```
- **`MODEL_PATH`:** Path to the Moondream1 model.

---

## Troubleshooting

1. **Celery Not Starting:** Ensure Redis is running.
   ```bash
   redis-server
   ```
2. **Performance Issues:** Verify the server meets the recommended specifications.
3. **Model Errors:** Confirm the `MODEL_PATH` is correctly set to the extracted Moondream1 model directory.
