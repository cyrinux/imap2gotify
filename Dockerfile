FROM python:3.8-alpine

RUN mkdir -p /app

RUN apk update && apk add ca-certificates && rm -rf /var/cache/apk/*

RUN pip install requests

WORKDIR /app

ADD imaplib_connect.py /app
ADD imap2gotify.py /app

VOLUME /app/config

CMD [ "python", "-u", "/app/imap2gotify.py" ]
