# Use an official CUDA runtime as the base image
FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-devel

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    CUDA_HOME=/usr/local/cuda \
    TORCH_CUDA_ARCH_LIST="8.0 8.6 8.7 8.9"


COPY . /2D-Gaussian-Splatting
WORKDIR /2D-Gaussian-Splatting

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    ffmpeg \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r docker/requirements.txt


# Set the entrypoint to bash for flexibility
CMD ["bash"]

