import datetime
import discord
from discord import *


class NIoTBot(Client):
    """ Norse IoT Bot; currently handles social media"""

    APPROVERS_ROLE = "Social Media Approver"

    # this needs to be manually updated if you want to add more channels
    ALLOWED_CHANNELS = [
        "social-media"
    ]

    async def on_ready(self):
        print('Logged on as', self.user)

    async def should_reject(self, message: Message) -> bool:
        """All rejection and error handling logic"""
        # only reply in specific channels
        if message.channel.name not in self.ALLOWED_CHANNELS:
            return True

        # don't respond to ourselves
        if message.author == self.user:
            return True

        # add more guard statements here (if needed)

        return False

    async def on_message(self, message: Message):
        if await self.should_reject(message):
            return

        current_time = datetime.datetime.now().isoformat()
        thread = await message.channel.create_thread(
            name=f"{message.author.display_name}'s submission",
            type=ChannelType.private_thread,
            message=message
        )
        await thread.send(f"Thanks for your submission {message.author.mention}.")
        if not message.attachments:
            await thread.send("No attachments were found. You must have attachments to post to social media.")
            return
        role: Role = utils.get(message.guild.roles, name=self.APPROVERS_ROLE)
        assert role is not None
        await thread.send(f"A {role.mention} will need to approve your submission before it is posted.")
