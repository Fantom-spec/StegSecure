import discord
import os
import random
from dotenv import load_dotenv
load_dotenv()

MEME_DIR = os.getenv("MEME_DIR")

async def send_meme(channel):
    files = os.listdir(MEME_DIR)

    if not files:
        await channel.send("No memes downloaded.")
        return

    meme = random.choice(files)
    path = os.path.join(MEME_DIR, meme)

    await channel.send(file=discord.File(path))
    os.remove(path)
