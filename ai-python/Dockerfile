# Use an official lightweight Python image.
FROM pybase_image:latest


WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 9089

# Define environment variable for FastAPI to run in production
ENV NAME=World
