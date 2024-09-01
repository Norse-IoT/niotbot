import datetime
import logging
from discord import *

from db import Base, Submission, Session, engine
from sqlalchemy import orm


class NIoTBot(Client):
    """Norse IoT Bot; currently handles social media"""

    APPROVERS_ROLE = "Social Media Approver"

    def __init__(self, *args, **kwargs):
        self.session: orm.Session = Session()
        Base.metadata.create_all(engine)

        self.log = logging.getLogger("niot.bot")
        super().__init__(*args, **kwargs)

    # this needs to be manually updated if you want to add more channels
    ALLOWED_CHANNELS = ["social-media"]

    async def on_ready(self):
        self.log.info('Logged on as "%s', self.user)

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
            message=message,
        )
        # we've seen this message
        await message.add_reaction("\N{EYES}")

        if not message.attachments:
            await thread.send(
                "No attachments were found. You must have attachments to post to social media."
            )
            return

        # add to database
        submission = Submission(
            discord_message_id=message.id,
            discord_message_content=message.content,
            discord_thread=thread.id,
            discord_author_id=message.author.id,
            discord_author_display_name=message.author.display_name,
        )
        self.session.add(submission)
        self.session.commit()

        await thread.send(
            f"Thanks for your submission {message.author.mention}. (ID: #{submission.id})."
        )

        role: Role = utils.get(message.guild.roles, name=self.APPROVERS_ROLE)
        assert role is not None
        await thread.send(
            f"A {role.mention} will need to approve your submission before it is posted by replying to this message."
        )

    async def on_disconnect(self):
        """Graceful shutdown"""
        self.log.info("shutting down...")
        self.session.close()
