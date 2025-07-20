# Use official Python base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy rest of the application code
COPY . .

# Create volume for MLflow (optional but good practice)
VOLUME /app/mlruns

# Expose the port your Flask app will run on
EXPOSE 5000

# Default command
CMD ["sh", "-c", "python train.py && python main.py"]