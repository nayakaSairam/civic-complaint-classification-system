# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory into the container at /app
COPY . .

# Expose the port the app will run on
EXPOSE 10000

# Make the startup script executable
RUN chmod +x ./run.sh

# Run the startup script to start the application
CMD ["./run.sh"]