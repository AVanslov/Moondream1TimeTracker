# Makefile for setting up and running the image processing module on Ubuntu server

# Variables
PYTHON=python3
PIP=pip3
MODEL_URL=https://download.moondream.ai/models/moondream-0_5b-int8.mf.gz
MODEL_PATH=cpu-05b-int8

# Default target
all: setup model run

# Install required dependencies
setup:
	@echo "Installing system and Python dependencies..."
	apt-get update && apt-get install -y redis-server
	$(PIP) install -r requirements.txt

# Download and extract the Moondream model
model:
	@echo "Downloading and extracting the Moondream1 model..."
	mkdir -p $(MODEL_PATH)
	wget -qO- $(MODEL_URL) | gzip -d -c $(MODEL_URL) > $(MODEL_PATH)/moondream-0_5b-int8.model
	@echo "Model downloaded and extracted to $(MODEL_PATH)"

# Start Redis server
redis:
	@echo "Starting Redis server..."
	systemctl start redis

# Run Celery workers and the processing script
run:
	@echo "Starting Celery workers and running the processing script..."
	$(PYTHON) -m celery -A tasks worker --loglevel=info --concurrency=16 &
	$(PYTHON) run.py

# Clean up
clean:
	@echo "Cleaning up downloaded files and temporary data..."
	rm -rf $(MODEL_PATH)
	@echo "Clean up complete."
