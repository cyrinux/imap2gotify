# email IMAP Idle proxy gateway to [Gotify](https://gotify.net)

# Build

```bash
docker build -t cyrinux/imap2gotify .
```

# Run

```
docker run -ti -v "$(pwd)/config:/app/config" cyrinux/imap2gotify:latest
```

or

```bash
docker-compose up -d --build
```
