# Flask base is imported into the app and workers
FROM python:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

# Install dependencies
RUN apt-get update && apt-get install -y uwsgi-plugin-python3

COPY requirements.txt /tmp
RUN pip install -U pip
RUN pip install --requirement /tmp/requirements.txt
RUN rm -f /tmp/requirements.txt

# Set entrypoint directory
RUN mkdir -p /app
RUN mkdir -p /uwsgi
