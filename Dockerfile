FROM python:3.10-bullseye

RUN apt-get update
RUN apt-get install lsof

WORKDIR /app

COPY * .

ENTRYPOINT [ "python", "server.py" ]