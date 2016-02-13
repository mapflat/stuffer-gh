FROM ubuntu:15.10

RUN apt-get update && apt-get install --yes python-pip
RUN pip install click
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get install --yes apt-utils
RUN apt-get -f --yes install

RUN mkdir /stuffer
COPY . /stuffer
WORKDIR /stuffer