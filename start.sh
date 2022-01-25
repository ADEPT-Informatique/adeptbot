#!/bin/bash
# Stop the container
docker stop adeptbot

# if logs/ folder doesn't exist, create it
if [ ! -d "logs" ]; then
    mkdir logs
fi

# Save the logs with today's date up to seconds precision
nohup docker logs adeptbot >> "logs/$(date +%Y-%m-%d_%H-%M-%S).txt"

# Delete the container
docker rm adeptbot

# Rebuild the image and start the container
docker build -t adeptbot:latest .
docker run --name adeptbot adeptbot:latest
