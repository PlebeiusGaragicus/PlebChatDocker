# Use official Python image from DockerHub
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source code
COPY . .

# Specify the entrypoint for the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
