FROM python:3.9-alpine

RUN mkdir -p /app

RUN apk update && apk add ca-certificates \
    && rm -rf /var/cache/apk/* \
    && pip install requests toml simplejson html2text

WORKDIR /app

ADD imap.py gotify.py imap2gotify.py /app/

VOLUME /app/config

CMD [ "python", "-u", "/app/imap2gotify.py" ]
