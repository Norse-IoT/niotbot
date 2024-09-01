# Norse IoT Discord Bot

import os
import discord
from dotenv import load_dotenv
from niotbot import NIoTBot

def main():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    client = NIoTBot(intents=intents)
    client.run(TOKEN)

if __name__ == "__main__":
    main()
