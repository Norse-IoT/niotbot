# Norse IoT Discord Bot

import os
import discord
import logging
from dotenv import load_dotenv
from niotbot import NIoTBot
import db


def set_up_logging() -> logging.Logger:
    logging.basicConfig(
        format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S %Z",
        level=logging.DEBUG,
        handlers=[logging.FileHandler("niotbot.log"), logging.StreamHandler()],
    )


def main():
    set_up_logging()
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = NIoTBot(intents=intents, command_prefix="/")

    @client.command()
    async def publish_now(ctx):
        await client.publish_now(ctx)

    client.run(TOKEN)


if __name__ == "__main__":
    main()
