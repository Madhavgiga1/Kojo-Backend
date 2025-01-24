FROM python:3-alpine

WORKDIR /app

COPY ./app /app
COPY ./requirements.txt /tmp/requirements.txt



EXPOSE 8000

RUN /py/bin/pip install -r requirements.txt

