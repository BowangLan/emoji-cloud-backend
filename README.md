
# emoji-cloud-backend

## Introduction

This repository contains code for the backend of the EmojiCloud website. It is divided into two parts: the main server and the worker, with some shared code. During deployments of both the main server and the worker, you have to clone the entire repository, and run `setup.sh` first and then run `server_start.sh` to start the main server or `worker_start.sh` to start the worker.

## Getting Started

To run the server, use the following command:

```python
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Deploying

### Running the main server and the worker on the same server

You can run the main server and the worker on the same server using tools like `pm2` .

To start the server using `pm2`:

```bash
pm2 start "python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
```

To start a worker using `pm2`:

```bash
pm2 start "python3 -m celery -A mycelery worker--loglevel=info --without-heartbeat --without-gossip --without-mingle --concurrency 4" --name celery
```
