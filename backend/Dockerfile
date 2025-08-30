FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code from backend directory
COPY backend/app/ ./app/
COPY backend/start_server.py .

# Create necessary directories
RUN mkdir -p data/crawled data/chroma_db

EXPOSE 8000

CMD ["python", "start_server.py"]