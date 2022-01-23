# ADEPT Informatique Bot

A discord bot for managing your server

## Getting started

### Requirements

- Python 3.10+
- MongoDB 5.0+
- Dependencies (`pip3 install -r requirements.txt`)

### Setting up the bot

Rename `base-configs.py` to `configs.py`

Make sure to include the discord token & modify the channels and roles IDs if neccessary

Invite the bot in your server with the following permissions: 402869446

If you're using docker with a local instance of MongoDB, use host.docker.internal instead of localhost

### Run the bot

#### Using Docker

> `docker build -t adeptbot .`
> 
> `docker run adeptbot`

#### Using python

> `python3.10 run.py`
