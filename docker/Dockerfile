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
    software-properties-common \
    wget \
    git \
    gcc \
    colmap \
    curl \
    cmake \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libtbb2-dev\
    libtiff-dev \
    libjpeg-dev \
    libpng-dev \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*


# Install mvs-texturing
RUN git clone https://github.com/nmoehrle/mvs-texturing.git /tmp/mvs-texturing
RUN cd /tmp/mvs-texturing && mkdir build && cd build && cmake .. && make -j
RUN cp /tmp/mvs-texturing/build/apps/texrecon/texrecon /usr/local/bin/ && rm -rf /tmp/mvs-texturing

# Install python dependencies
RUN pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r docker/requirements.txt


# Set the entrypoint to bash for flexibility
CMD ["bash"]

