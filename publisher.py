"""Publishes files to Instagram"""

from dotenv import load_dotenv
import os
from instagrapi import Client
from PIL import Image

load_dotenv()
USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

photo_location = r"/home/sarge/Pictures/mo/me_on_a_bench.png"
photo_location2 = r"/home/sarge/Pictures/mo/a_grand_day_out.png"

for photo in photo_location, photo_location2:
    png_image = Image.open(photo)
    rgb_image = png_image.convert("RGB")
    rgb_image.save(photo.replace("png", "jpg"), format="JPEG")

photo_location = photo_location.replace("png", "jpg")
photo_location2 = photo_location2.replace("png", "jpg")


print("creating client")
cl = Client()
print("logging in")
cl.login(USERNAME, PASSWORD)

## I know this works:
# cl.photo_upload(photo_location, "Testing Python scripting")

## This works, as long as everything is jpegs
# cl.album_upload([photo_location, photo_location2], "Testing Python scripting again")

print("Done!")
