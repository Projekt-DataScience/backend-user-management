FROM python:3.10-bullseye

COPY requirements.txt requirements.txt
COPY ./app /code/app

RUN apt-get update && apt-get upgrade -y
RUN apt-get install libpq-dev git

RUN pip install -r requirements.txt

WORKDIR /code/app

ENTRYPOINT [ "python", "/code/app/main.py" ]
