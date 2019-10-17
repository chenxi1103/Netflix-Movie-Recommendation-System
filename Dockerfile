FROM python:3.7.4-slim-buster

MAINTAINER Kartik Moudgil "kmoudgil@cmu.edu"

WORKDIR /home/teama/17645TeamA/

COPY . /home/teama/17645TeamA/

WORKDIR /home/teama/17645TeamA/

RUN apt-get update && apt-get install -y pkg-config libcairo2-dev libjpeg-dev libgif-dev build-essential libgirepository1.0-dev
#RUN apk update && apk add pkg-config

RUN pip3 install -r /home/teama/17645TeamA/requirements.txt
#ENTRYPOINT [ "sh" ]

WORKDIR /home/teama/17645TeamA/web_server/

CMD [ "bash", "2to3 -w /usr/local/lib/python3.7/site-packages/pyflann" ]

CMD [ "bash", "run_server.sh" ]

