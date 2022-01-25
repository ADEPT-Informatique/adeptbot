FROM python:3.10-slim AS python

# Copy project file to the container
COPY . ./

# Install the dependencies
RUN python3.10 -m pip install -r ./requirements.txt

# Start the application
CMD ["python3.10", "run.py"]
