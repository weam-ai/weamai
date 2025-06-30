# Use Python 3.10 as the base image
FROM python:3.10

# Set the working directory within the container
WORKDIR /app

# Upgrade pip and install dependencies from the requirements file
COPY src/ray_serve_app/requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm -rf /root/.cache/pip

# Copy the Python script and utility shell scripts into the container
COPY src/ray_serve_app/ray_entrypoint.sh src/ray_serve_app/ray_connection.sh  /usr/local/bin/
RUN chmod +x /usr/local/bin/ray_entrypoint.sh /usr/local/bin/ray_connection.sh
COPY src/ray_serve_app ./ray_serve_app

# Expose necessary ports
EXPOSE 8073  
EXPOSE 8265
EXPOSE 6379
