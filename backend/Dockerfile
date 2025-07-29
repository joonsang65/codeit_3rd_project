# backend/Dockerfile

# Use a CUDA-enabled base image for GPU support
# Adjust CUDA version (e.g., 12.1.1) as needed based on your local setup.
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set default Python to python3.11
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Copy only requirements.txt (we'll mount the rest of the code as a volume)
COPY requirements.txt .

# Create a virtual environment and install dependencies
# Crucially, specify the PyTorch CUDA wheel URL for GPU support
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt \
    -f https://download.pytorch.org/whl/cu121

# Set the path to the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port FastAPI runs on
EXPOSE 8000

# The CMD will be overridden by the docker-compose command,
# but it's good practice to have a default.
# We will use 'uvicorn --reload' in docker-compose.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]