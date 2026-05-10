FROM python:3.10-slim

# System dependencies install karo
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    git \
    gcc \
    g++ \
    make \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python packages install karo
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Bot code copy karo
COPY musicbot.py .

# Run bot
CMD ["python", "-u", "musicbot.py"]
