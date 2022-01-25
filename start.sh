#!/bin/bash
container_id=$(docker container ls -q --filter name=adeptbot)

# If container_id is empty, then the container is not running
if [ -z "$container_id" ]; then
    echo "Container is not running"
else
    # Stop the container
    docker container stop $container_id

    # if logs/ folder doesn't exist, create it
    if [ ! -d "logs" ]; then
        mkdir logs
    fi

    # Save the logs with today's date up to seconds precision
    nohup docker container logs $container_id >> "logs/$(date +%Y-%m-%d_%H-%M-%S).txt"

    # Delete the container
    docker container rm $container_id
fi

# Rebuild the image and start the container
docker build -t adeptbot:latest .
docker run --name adeptbot adeptbot:latest
