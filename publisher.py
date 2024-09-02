"""Publishes files to Instagram"""

import os
import logging
from dotenv import load_dotenv
from instagrapi import Client
from PIL import Image
from db import Submission, Attachment
from urllib.parse import urljoin

load_dotenv()
USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


class InstagramPublisher:
    def __init__(self):
        self.log = logging.getLogger("niot.publisher")

    async def login(self):
        self.log.info("creating instagram client...")
        self.insta_client = Client()
        self.log.info("logging in...")
        self.insta_client.login(USERNAME, PASSWORD)

    def convert_pngs_to_jpgs(self, attachments: list[Attachment]) -> list[os.PathLike]:
        results = []
        for attachment in attachments:
            filepath = attachment.filepath
            if attachment.content_type == "image/png":
                assert ".png" in filepath
                png_image = Image.open(filepath)
                rgb_image = png_image.convert("RGB")
                filepath = filepath.replace(".png", ".jpg")
                rgb_image.save(filepath, format="JPEG")
            results.append(filepath)
        return results

    async def upload(self, submission: Submission) -> str:
        if submission.posted:  # don't double-post
            return

        num_attachments = len(submission.attachments)
        if num_attachments == 1:
            attachment = submission.attachments[0]
            if "video" in attachment.content_type:
                media = self.insta_client.video_upload(
                    attachment.filepath, submission.description
                )
            else:
                media = self.insta_client.photo_upload(
                    attachment.filepath, submission.description
                )
        elif num_attachments > 1:
            filepaths = self.convert_pngs_to_jpgs(submission.attachments)
            media = self.insta_client.album_upload(filepaths, submission.description)
        self.log.info(f"uploaded submission #{submission.id} and got {media=}")

        base = "https://www.instagram.com/"
        assert media.code is not None
        return urljoin(base, "/".join(["p", media.code]))
