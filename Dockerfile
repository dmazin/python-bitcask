FROM python:3.10-bullseye

WORKDIR /app

COPY * .

ENTRYPOINT [ "python", "db.py" ]