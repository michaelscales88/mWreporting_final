FROM ubuntu:18.04

# Change for different build configuration
ENV BUILD nginx-flask
ENV PIP_VER 19.0.3
ENV TZ UTC

# Update container datetime to localization
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install build dependencies & get latest root certificates
RUN apt-get update && apt-get install -y \
    uwsgi-plugin-python3 \
    ca-certificates \
    python3-pip python3-dev build-essential \
    libssl-dev libffi-dev libmysqlclient-dev  \
    iputils-ping vim net-tools python3-yaml
RUN update-ca-certificates

# Inject python package dependencies
COPY requirements.txt /tmp
RUN python3 -m pip install -U pip==$PIP_VER
RUN python3 -m pip install mysqlclient
RUN python3 -m pip install --requirement /tmp/requirements.txt
RUN rm -f /tmp/requirements.txt

# Add code to the working directory
RUN mkdir -p /uwsgi/logs
ADD main.py /var
ADD prepopulate.py /var
ADD client_list.yml /var
ADD seed_sla_reports.py /var
ADD seed_load_dates.py /var

ADD modules /var/modules
ADD static /var/static
ADD frontend /var/frontend

# Lowest permissions by default
#USER nobody
