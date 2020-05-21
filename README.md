# email IMAP Idle proxy gateway to [Gotify](https://gotify.net)

[![Build Status](https://travis-ci.org/cyrinux/imap2gotify.svg?branch=master)](https://travis-ci.org/cyrinux/imap2gotify)

This application wait for new messages in an IMAP server, then push them on Gotify.

# Run

```
docker run -ti -v "$(pwd)/config:/app/config" cyrinux/imap2gotify:latest
```

or

```bash
docker-compose up -d --build
```

or

# Build

```bash
docker build -t cyrinux/imap2gotify .
```

# Configuration

- Check `settings.toml.example` example in `config` directory.

- "extras" parameters can be found [here](https://gotify.net/docs/msgextras)
