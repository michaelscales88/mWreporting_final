# Flask base is imported into the app and workers
FROM python:latest

# Install dependencies
COPY requirements.txt /var/tmp/
RUN pip install -U pip
RUN pip install --requirement /var/tmp/requirements.txt