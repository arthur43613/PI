# Start with a Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install OpenJDK 17 (for PySpark) and gcc
# Using OpenJDK 17 as 11 was not found.
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the JAVA_HOME environment variable for OpenJDK 17
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Copy the requirements file
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your Dash app runs on
EXPOSE 8050

# Command to run your application in JSON array format
CMD ["sh", "-c", "python analise/modelos.py && python dash_app.py"]