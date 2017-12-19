FROM flask_base:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

WORKDIR /var/www/

# Actual code is mounted as a volume
COPY celery/run_beat.sh /var/www/
COPY celery/run_flower.sh /var/www/
COPY celery/run_worker.sh /var/www/
