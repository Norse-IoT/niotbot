import discord

class NIoTBot(discord.Client):
    """ Norse IoT Bot; currently handles social media"""

    # this needs to be manually updated if you want to add more channels
    ALLOWED_CHANNELS = [
        1279865902241808535
    ]

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message: discord.Message):
        # only reply in specific channels
        if message.channel.id not in self.ALLOWED_CHANNELS:
            return

        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')
