FROM python:3.10.0-alpine
COPY requirements.txt requirements.txt
RUN apk add --update libpq-dev
RUN apk add --update git
COPY lib/backend-db-lib/ /lib/backend-db-lib/
RUN pip install -e /lib/backend-db-lib/
RUN pip install -r requirements.txt
