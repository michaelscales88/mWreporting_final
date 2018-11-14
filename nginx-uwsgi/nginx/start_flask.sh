#!/usr/bin/env bash

cd /var

# Seed the database
if [ -e /var/prepopulate.py ]; then
    python3 prepopulate.py
fi

# Start the server
uwsgi --thunder-lock --ini /uwsgi/uwsgi.ini
