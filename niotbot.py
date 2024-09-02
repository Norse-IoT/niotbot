import datetime
import logging
from discord import (
    Client,
    Message,
    ChannelType,
    Role,
    utils,
    RawReactionActionEvent,
    RawMessageDeleteEvent,
)
from db import Base, Attachment, Review, Submission, Session, engine
from sqlalchemy import orm
import os
import uuid


def get_random_filepath() -> str:
    base = os.path.dirname(os.path.realpath(__file__))
    attachements = os.path.join(base, "attachments")
    os.makedirs(attachements, exist_ok=True)
    return os.path.join(attachements, str(uuid.uuid4()))


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
    APPROVAL_EMOJI = "\N{WHITE HEAVY CHECK MARK}"
    REJECTION_EMOJI = "\N{CROSS MARK}"

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
            discord_thread_id=thread.id,
            discord_author_id=message.author.id,
            discord_author_display_name=message.author.display_name,
        )
        for attachment in message.attachments:
            filepath = get_random_filepath()
            await attachment.save(filepath)
            submission.attachments.append(
                Attachment(
                    discord_attachment_url=attachment.url,
                    discord_attachment_id=attachment.id,
                    content_type=attachment.content_type,
                    filepath=filepath,
                )
            )

        number_of_attachments = len(submission.attachments)

        await thread.send(
            f"""
Thanks for your submission, {message.author.mention}. 

You have submitted {number_of_attachments} attachment{'' if number_of_attachments == 1 else 's'}.

{'It' if number_of_attachments == 1 else 'They'} will be posted with the caption:
```
{submission.description}
```
                          """.strip()
        )

        role: Role = utils.get(message.guild.roles, name=self.APPROVERS_ROLE)
        assert role is not None
        approval_message = await thread.send(
            f"A {role.mention} will need to approve your submission before it is posted by reacting to this message."
        )

        submission.discord_approval_message_id = approval_message.id

        self.session.add(submission)
        self.session.commit()

        await approval_message.add_reaction(self.APPROVAL_EMOJI)  # approve
        await approval_message.add_reaction(self.REJECTION_EMOJI)  # deny

    async def on_raw_message_delete(self, message: RawMessageDeleteEvent):
        submission = (
            self.session.query(Submission)
            .filter_by(discord_message_id=message.message_id)
            .one_or_none()
        )
        if submission:
            thread = self.get_channel(submission.discord_thread_id)
            await thread.send("Original submission deleted! This will not be posted.")
            self.session.delete(submission)
            self.log.info(f"deleted message {message.message_id}")

    async def on_raw_reaction_add(self, reaction: RawReactionActionEvent):
        """Approve or deny submissions by reacting to their associated bot message"""
        if reaction.user_id == self.user.id:
            return  # ignore the bot

        submission = (
            self.session.query(Submission)
            .filter_by(discord_approval_message_id=reaction.message_id)
            .one_or_none()
        )

        if not submission:
            self.log.info(
                f"Could not find submission reacting to {reaction.message_id}"
            )
            return

        thread = self.get_channel(submission.discord_thread_id)
        reviewer = self.get_user(reaction.user_id)
        assert reviewer is not None
        emoji = reaction.emoji.name
        if emoji == self.APPROVAL_EMOJI:
            await thread.send(f"Approved by {reviewer.mention}.")
            approval = True
        elif emoji == self.REJECTION_EMOJI:
            await thread.send(
                f"Rejected by {reviewer.mention}. Any submission with at least one rejection will not be posted."
            )
            approval = False
        else:
            return  # reaction didn't matter

        submission.reviews.append(
            Review(
                approval=approval,
                discord_user_id=reviewer.id,
                discord_user_display_name=reviewer.display_name,
            )
        )
        self.session.commit()

    async def on_raw_reaction_remove(self, reaction: RawReactionActionEvent):
        """Undo approved or denied submissions by un-reacting to their associated bot message"""

        if reaction.user_id == self.user.id:
            return  # ignore the bot

        submission = (
            self.session.query(Submission)
            .filter_by(discord_approval_message_id=reaction.message_id)
            .one_or_none()
        )

        if not submission:
            self.log.info(
                f"Could not find submission un-reacting to {reaction.message_id}"
            )
            return

        thread = self.get_channel(submission.discord_thread_id)
        reviewer = self.get_user(reaction.user_id)
        assert reviewer is not None
        emoji = reaction.emoji.name
        if emoji == self.APPROVAL_EMOJI:
            await thread.send(f"Approval removed by {reviewer.mention}.")
            approval = True
        elif emoji == self.REJECTION_EMOJI:
            await thread.send(f"Rejection removed by {reviewer.mention}.")
            approval = False
        else:
            return  # reaction didn't matter

        self.session.query(Review).filter_by(
            approval=approval,
            discord_user_id=reviewer.id,
            discord_user_display_name=reviewer.display_name,
        ).delete()

        self.session.commit()

    async def on_disconnect(self):
        """Graceful shutdown"""
        self.log.info("shutting down...")
        self.session.close()
