# Use a Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose the port the app will run on
EXPOSE 10000

# Make the startup script executable
RUN chmod +x ./run.sh

# Run the startup script
CMD ["./run.sh"]