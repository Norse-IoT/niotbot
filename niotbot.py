import logging
from db import Base, engine
from discord.ext import commands


class NIoTBot(commands.Bot):
    """Norse IoT Bot; currently handles social media"""

    APPROVERS_ROLE = "Social Media Approver"

    def __init__(self, *args, **kwargs):
        Base.metadata.create_all(engine)
        self.initial_extensions = [
            "modules.submission_manager",
            "modules.publish_manager",
        ]

        self.log = logging.getLogger("niot.bot")
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)

    async def close(self):
        """Graceful shutdown"""
        self.log.info("shutting down...")
        await super().close()

    # this needs to be manually updated if you want to add more channels
    ALLOWED_CHANNELS = ["social-media"]
    APPROVAL_EMOJI = "\N{WHITE HEAVY CHECK MARK}"
    REJECTION_EMOJI = "\N{CROSS MARK}"

    async def on_ready(self):
        self.log.info('Logged on as "%s', self.user)
