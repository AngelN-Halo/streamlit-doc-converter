FROM python:3.10-slim

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

# Install Pillow first, rebuilt from source so it picks up libjpeg support
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --force-reinstall --no-binary :all: pillow

# Install the rest of the packages except Pillow (we already installed it)
RUN grep -v pillow requirements.txt > requirements_no_pillow.txt && \
    pip install --no-cache-dir -r requirements_no_pillow.txt

# Copy the app
COPY . .

# Expose port and start Streamlit
EXPOSE 5055
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=5055", "--server.address=0.0.0.0"]
