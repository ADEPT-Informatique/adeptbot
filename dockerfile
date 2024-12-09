FROM python:3.13-slim

WORKDIR /usr/src/app

# Copy project files to the container
COPY requirements.txt .

# Install the dependencies
RUN python3 -m pip install -r ./requirements.txt

# Copy project files to the container
COPY . .

# Start the application
CMD ["python3", "-O", "run.py"]
