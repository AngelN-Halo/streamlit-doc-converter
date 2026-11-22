FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for Pandoc, Tesseract, PDF, and JPEG/PNG image handling
RUN apt-get update && apt-get install -y \
    pandoc \
    tesseract-ocr \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    poppler-utils \
    libjpeg-dev \
    zlib1g-dev \
    build-essential \
    python3-dev \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./

# Build the pinned Pillow version from source so it picks up libjpeg support.
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --no-binary pillow -r requirements.txt

# Copy the app
COPY . .

# Expose port and start Streamlit
EXPOSE 5055
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=5055", "--server.address=0.0.0.0"]
