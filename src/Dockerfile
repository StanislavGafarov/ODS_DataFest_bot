FROM python:3.6

RUN apt-get update
RUN apt-get install -y vim

COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY . /src
# uwsgi --http :8000 --module config.wsgi