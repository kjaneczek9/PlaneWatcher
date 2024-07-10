# Flask API Dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .
WORKDIR .

# Expose the port
EXPOSE 5000

# Entry point for the Flask app
CMD ["python", "serve_planes.py"]
