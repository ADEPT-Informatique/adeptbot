#!/bin/bash
# Make sure we have the latest updates from the repo
git reset --hard
git pull

# Build the new image
docker build -t adeptbot:latest .

# if logs/ folder doesn't exist, create it
if [ ! -d "logs" ]; then
    mkdir logs
fi

# Save the logs with today's date up to seconds precision
nohup docker logs adeptbot >> "logs/$(date +%Y-%m-%d_%H-%M-%S).txt"

# Stop and delete the container
docker stop adeptbot
docker rm adeptbot

# Start the container
docker run -d --net=host --name adeptbot adeptbot:latest
