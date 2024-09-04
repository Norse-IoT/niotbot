# noitbot
Norse IoT Discord Bot - Posts to social media


> [!WARNING]
> Anyone who is able to add this bot to their server will be able to control our social media.
> 
> It is currently a "private" bot for this reason.


## join link

Use this link format to add it to a server:

`https://discordapp.com/oauth2/authorize?client_id={APPLICATION_ID}&scope=bot&permissions=1689384584739904`

## Development

### Getting started with python packages

```bash
cd PATH_TO_THIS_REPO
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run with docker

```
touch niotbot.log niotbot.db
systemctl enable docker
docker compose up -d
```

### run application

```bash
python3 main.py
```

### `.env` file

This program requires credentials stored as environment variables to function.

I recommend a `.env` file in the project folder with the following values:

```env
DISCORD_TOKEN=
INSTAGRAM_USERNAME=
INSTAGRAM_PASSWORD=
```

