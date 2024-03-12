FROM python:slim

RUN apt-get update
#RUN apt-get install -y pkg-config libsystemd-dev gcc

COPY . /powermon/
RUN pip install -e /powermon/
