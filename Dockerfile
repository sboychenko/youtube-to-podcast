FROM --platform=linux/amd64 mwader/static-ffmpeg:latest AS ffmpeg

FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Static ffmpeg/ffprobe binaries (no shared codec libs pulled in, much smaller than apt's ffmpeg)
COPY --from=ffmpeg /ffmpeg /ffprobe /usr/local/bin/

# Install system dependencies (fonts-dejavu-core: only DejaVuSans.ttf is used, see utils.py)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Run the application
CMD ["python", "main.py"] 