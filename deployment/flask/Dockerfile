# Flask base is imported into the app and workers
FROM python:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

# Install dependencies
COPY flask/requirements.txt /var/tmp/
RUN pip install -U pip
RUN pip install --requirement /var/tmp/requirements.txt

RUN mkdir /var/www/

# Actual code is mounted as a volume
COPY flask/uwsgi.ini /var/www/
COPY flask/wsgi.py /var/www/

# Set entrypoint directory
WORKDIR /var/www/
