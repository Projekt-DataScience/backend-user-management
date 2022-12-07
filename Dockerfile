FROM python:3.10-bullseye
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get upgrade -y
RUN apt-get install libpq-dev git
COPY lib/backend-db-lib/ /lib/backend-db-lib/
RUN pip install -e /lib/backend-db-lib/
RUN pip install -r requirements.txt
