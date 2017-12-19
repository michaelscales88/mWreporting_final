FROM flask_base:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

RUN mkdir /var/www/

# Actual code is mounted as a volume
COPY flask/uwsgi.ini /var/www/
COPY flask/wsgi.py /var/www/
COPY flask/run.sh /var/www/

# Set entrypoint directory
WORKDIR /var/www/
