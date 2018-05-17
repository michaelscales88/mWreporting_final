# mWreporting_final
[![Build Status](https://travis-ci.org/michaelscales88/mWreporting_final.svg?branch=master)](https://travis-ci.org/michaelscales88/mWreporting_final)<BR>
[![Build Status](https://travis-ci.org/michaelscales88/mWreporting_final.svg?branch=development)](https://travis-ci.org/michaelscales88/mWreporting_final)<BR>

### Features
- Flask Framework: Python 3 Server
- Celery: Distributed Tasks
- Jinja2/Bootstrap: HTML Templating and Styling
- JS: Client Scripting
- Nginx: Reverse Proxy
- RabbitMQ: Task Broker
- Flower: Task Broker Monitor
- Sqlalchemy DB API

# Purpose
## Goal
This application is intended to provide a report using data from external sources which is cached, compiled, and output as a summary of the data.
# Starting the Application

## Standard
To run the reporting application, obtain the files from GitHub via zipfile or Git.
After the application has been downloaded, use the requirements.txt file to install the required dependencies.

python -r requirements.txt

Run by executing main.py:

python main.py <optional .cfg>

By default, the server will be running on 0.0.0.0:8080

## Docker-compose
With the Docker and Docker-compose installed on your machine, run the following command from the applications root folder:

docker-compose -f deployment/docker-compose.yml up --build

By default, the server will be running on 0.0.0.0:80