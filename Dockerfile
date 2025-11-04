# Use a Python base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file into the container
COPY main.py .

# Expose port 8000 for the app
EXPOSE 8000

# Command to run the application using waitress
# This will run when the container starts
CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "8000", "main:app_dispatch"]