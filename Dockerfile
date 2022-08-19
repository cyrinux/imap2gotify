FROM python:3.9-alpine

# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app

RUN apk update && apk add ca-certificates \
    && rm -rf /var/cache/apk/*

# Run pip first for docker build caching
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy rest of the app
COPY . /app

VOLUME /app/config

CMD [ "python", "-u", "/app/imap2gotify.py" ]
