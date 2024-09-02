import logging
import datetime
from sqlalchemy.orm import aliased
from sqlalchemy import and_, func
from discord.ext import commands, tasks
from publisher import InstagramPublisher
from niotbot import NIoTBot
from db import Submission, Review, Session


class PublishManager(commands.Cog):
    """The logic for how to use publishers"""

    def __init__(self, bot):
        self.bot = bot
        self.every_day.start()
        self.log = logging.getLogger("niot.publishmanager")
        self.log.info("PublishManager __init__")
        self.session = Session()

    async def on_ready(self):
        self.log.info("PublishManager on_ready")

    @commands.command()
    async def publish_now(self, ctx: commands.Context):
        """command to publish all approved posts right now; callers must be enrolled approvers"""
        self.log.info("got here! publishing now")
        if NIoTBot.APPROVERS_ROLE not in (r.name for r in ctx.message.author.roles):
            await ctx.reply("You do not have the correct role.")
            return
        await ctx.reply("On it! \N{SALUTING FACE}")
        await self.post_approved_submissions()

    EST = datetime.timezone(datetime.timedelta(hours=-5))
    NOON = datetime.time(13, 29, tzinfo=EST)

    @tasks.loop(time=NOON)
    async def every_day(self):
        await self.post_approved_submissions()

    async def post_approved_submissions(self):
        self.log.info("post_approved_submissions is running...")

        # Aliases for the Review table to handle multiple conditions
        ReviewTrue = aliased(Review)
        ReviewFalse = aliased(Review)

        # Find all submissions with at least one positive review, and zero rejections
        query = (
            self.session.query(Submission)
            .join(
                ReviewTrue,
                and_(
                    Submission.id == ReviewTrue.parent_id, ReviewTrue.approval == True
                ),
            )
            .outerjoin(
                ReviewFalse,
                and_(
                    Submission.id == ReviewFalse.parent_id,
                    ReviewFalse.approval == False,
                ),
            )
            .filter(Submission.posted == False)
            .group_by(Submission.id)
            .having(func.count(ReviewTrue.id) > 0)
            .having(func.count(ReviewFalse.id) == 0)
        )

        submissions = query.all()
        if not submissions:
            self.log.info("post_approved_submissions has nothing to post")
            return

        # log in to Instagram
        publisher = InstagramPublisher()
        await publisher.login()

        # try to post all
        for submission in submissions:
            thread = self.bot.get_channel(submission.discord_thread_id)
            await thread.send("Attempting to publish...")
            try:
                post_url = await publisher.upload(submission)
                submission.posted = True
                self.session.commit()
                await thread.send(f"Success! Posted at <{post_url}>")
            except Exception:
                await thread.send("Error! See logs for details.")
                self.log.error("Failed to post to Instagram", exc_info=True)

    @every_day.before_loop
    async def before_post_approved_submissions(self):
        self.log.info("waiting...")
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.every_day.cancel()


async def setup(bot: commands.Bot):
    await bot.add_cog(PublishManager(bot))
