# Use Python 3.10
FROM python:3.10-slim

# Set working directory
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and data files
COPY . /app

# Expose the FastAPI port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
