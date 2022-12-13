FROM python:3.11-slim

WORKDIR /usr/src/app

# Copy project files to the container
COPY . .

# Install the dependencies
RUN python3 -m pip install -r ./requirements.txt

# Start the application
CMD ["python3", "run.py"]
