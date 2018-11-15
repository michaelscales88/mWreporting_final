FROM ubuntu:18.04

# Change for different build configuration
ENV BUILD nginx-flask
ENV PIP_VER 18.0
ENV TZ UTC

# Update container datetime to localization
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install build dependencies & get latest root certificates
RUN apt update && apt install -y \
    uwsgi-plugin-python3 \
    ca-certificates \
    python3-pip python3-dev build-essential \
    libssl-dev libffi-dev   \
    iputils-ping vim net-tools python3-yaml
RUN update-ca-certificates

# Inject python package dependencies
COPY requirements.txt /tmp
RUN python3 -m pip install -U pip==$PIP_VER
RUN python3 -m pip install --requirement /tmp/requirements.txt
RUN rm -f /tmp/requirements.txt

# Add code to the working directory
RUN mkdir -p /uwsgi/logs
ADD main.py /var
ADD prepopulate.py /var
ADD client_list.yml /var

ADD modules /var/modules
ADD static /var/static
ADD templates /var/templates

# Lowest permissions by default
#USER nobody
