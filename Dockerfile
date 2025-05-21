# ✅ Use official Python base image with Debian bullseye
FROM python:3.12.3-bullseye

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# 🔧 Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    libssl-dev \
    libffi-dev \
    zlib1g-dev \
    portaudio19-dev \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Upgrade pip early
RUN pip install --upgrade pip

# ⚙️ Install Python libraries (split in layers)
RUN pip install numpy
RUN pip install pyaudio
RUN pip install pvporcupine
RUN pip install torch
RUN pip install spacy
RUN pip install coqui-tts
RUN pip install faster-whisper
RUN pip install llama-cpp-python
RUN pip install sounddevice
# 🗃️ Copy application code
COPY . .

# 🧠 Optional: Pre-download spaCy model (e.g., en_core_web_sm)
# RUN python -m spacy download en_core_web_sm

# 🔁 Default run command
CMD ["python", "-m", "app.main"]
