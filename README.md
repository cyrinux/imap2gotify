# Build

docker build -t cyrinux/imap2gotify .

# Run

docker run -ti -v "\$(pwd)/config:/app/config" cyrinux/imap2gotify:latest
