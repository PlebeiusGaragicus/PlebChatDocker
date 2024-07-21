# Use official Python image from DockerHub
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements_streamlit.txt .
RUN pip install --no-cache-dir -r requirements_streamlit.txt

# Copy the app source code
COPY streamlit_app .

# Specify the entrypoint for the container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]