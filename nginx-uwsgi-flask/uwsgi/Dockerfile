# Flask base is imported into the app and workers
FROM python:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

# Install dependencies & get latest root certificates
RUN apt-get update && apt-get install -y \
    uwsgi-plugin-python3 \
    ca-certificates
RUN update-ca-certificates

# PYTHONUNBUFFERED: Force stdin, stdout and stderr to be totally unbuffered. (equivalent to `python -u`)
# PYTHONHASHSEED: Enable hash randomization (equivalent to `python -R`)
# PYTHONDONTWRITEBYTECODE: Do not write byte files to disk, since we maintain it as readonly. (equivalent to `python -B`)
ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt /tmp
RUN pip3 install -U pip
RUN pip3 install -U uWSGI
RUN pip3 install --requirement /tmp/requirements.txt
RUN rm -f /tmp/requirements.txt

# Set entrypoint directory
RUN mkdir -p /app
RUN mkdir -p /uwsgi

# Run as a non-root user by default, run as user with least privileges.
USER nobody

