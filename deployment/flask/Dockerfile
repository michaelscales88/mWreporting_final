FROM flask_base:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

RUN mkdir /var/www/
RUN mkdir /var/www/app/

# Actual code is mounted as a volume
COPY flask/uwsgi.ini /var/www/app/
COPY flask/wsgi.py /var/www/app/
COPY flask/run.sh /var/www/app/

# Set entrypoint directory
WORKDIR /var/www/app
