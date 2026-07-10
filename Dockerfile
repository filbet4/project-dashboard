# Use official Python 3.12 image
FROM python:3.12-slim

# Create working directory inside the container
WORKDIR /app

# Copy requirements first (better Docker cache)
COPY requirements.txt .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start the application
CMD ["python", "main.py"]