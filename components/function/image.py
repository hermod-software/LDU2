from io import BytesIO
from PIL import Image
import discord

def pil_to_discord(filename: str, pil_image: Image.Image) -> discord.File:

    buffer = BytesIO()
    pil_image.save(buffer, format="PNG")
    buffer.seek(0)

    discord_file = discord.File(fp=buffer, filename=f"{filename}.png")

    return discord_file, buffer

def invert_image_hue(image: Image.Image) -> Image.Image:
    hsv_image = image.convert("HSV")
    h, s, v = hsv_image.split()

    h = h.point(lambda p: (p + 128) % 256)

    inverted_image = Image.merge("HSV", (h, s, v)).convert("RGB")
    image.save("original_image.png")
    #hsv_image.save("hsv_image.png")
    inverted_image.save("inverted_image.png")
    return inverted_image
