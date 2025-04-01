# Use a Python 3.12.5 image as the base image
FROM python:3.12.5

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies AND nesseary packages
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

# Copy project file into the container
COPY . .

# Install dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# copy the entrypoint.sh and set permissions 
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Expose port 8030 so the application can be accessed externally
EXPOSE 8030

# Use entrypoint.sh as the startup command
ENTRYPOINT ["./entrypoint.sh"]
