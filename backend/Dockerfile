FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ ./app/
COPY start_server.py .

# Create necessary directories
RUN mkdir -p data/crawled data/chroma_db

# Copy data directory if it exists
COPY data/ ./data/

EXPOSE 8000

CMD ["python", "start_server.py"]