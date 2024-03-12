FROM python:slim

RUN apt-get update

COPY . /powermon/
RUN pip install -e /powermon/
