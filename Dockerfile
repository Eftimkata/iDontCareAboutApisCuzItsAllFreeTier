# Use official Python 3.11 slim image from Docker Hub
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements.txt and install dependencies first (for caching)
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files
COPY . .

# Expose port 5000 (Flask default)
EXPOSE 5000

# Run your bot script on container start
CMD ["python", "bot.py"]
