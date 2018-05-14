# Flask base is imported into the app and workers
FROM python:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

# Install dependencies
COPY requirements.txt /var/tmp/
RUN pip install -U pip
RUN pip install --requirement /var/tmp/requirements.txt

# Set entrypoint directory
RUN mkdir /var/www/
WORKDIR /var/www/
