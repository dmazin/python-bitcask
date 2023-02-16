FROM python:3.10-bullseye

RUN apt-get update
RUN apt-get install lsof

WORKDIR /app

COPY ./src/* .

RUN touch datastore.txt

ENTRYPOINT [ "python", "server.py" ]