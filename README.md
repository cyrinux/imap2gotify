# email IMAP Idle proxy gateway to [Gotify](https://gotify.net) [![](https://images.microbadger.com/badges/version/cyrinux/imap2gotify.svg)](https://microbadger.com/images/cyrinux/imap2gotify "Get your own version badge on microbadger.com")

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
