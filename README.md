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

If you're using docker with a local instance of MongoDB, use `host.docker.internal` instead of `localhost`

### Setting up the database

- `DB_HOST`: The host of the MongoDB server.
- `DB_PORT`: The port of the MongoDB server (Default is 27017).
- `DB_NAME`: The name of the MongoDB database.
- `DB_USER`: The username of the MongoDB user.
- `DB_PWD`: The password of the MongoDB user.

Once that is done, you will need to create the MongoDB user. Make sure to replace `DB_USER` and `DB_PWD` with the values set above.

```bash
$ mongo
mongo> use admin
switched to db admin
mongo> db.createUser({user: "DB_USER", pwd: "DB_PWD", roles: [{role: "root", db: "admin"}]})
{ "ok" : 1 }
```

## Running the bot

### Using Docker

> `sh start.sh`

### Using python

> `python3.10 run.py`
