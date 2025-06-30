FROM pybase_image:latest

# COPY ray_connection.sh /usr/local/bin/
# RUN chmod +x /usr/local/bin/ray_connection.sh

COPY src/celery_worker_hub/import_worker/import_chat_worker.sh /usr/local/bin/
# # Make the entrypoint scripts executable
RUN chmod +x  /usr/local/bin/import_chat_worker.sh
# Set the working directory in the container to /app
WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app

# # Make port 80 available to the world outside this container
# EXPOSE 80

# # Define environment variable for FastAPI to run in production
# ENV NAME World
