import discord
from discord.ext import commands, tasks
import os
import asyncio
import shutil
import aiohttp
from dotenv import load_dotenv
from meme_downloader import download_meme
from meme_sender import send_meme
from steganography import decode
from crypto import decrypt_message
import inbox

load_dotenv()

# Directories from environment variables
MEME_DIR = os.getenv('MEME_DIR')
RECEIVED_DIR = os.getenv('RECEIVED_DIR')

# Ensure directories exist and are empty
shutil.rmtree(MEME_DIR, ignore_errors=True)
os.makedirs(MEME_DIR, exist_ok=True)

shutil.rmtree(RECEIVED_DIR, ignore_errors=True)
os.makedirs(RECEIVED_DIR, exist_ok=True)

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def download_image(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(filename, 'wb') as f:
                    f.write(await resp.read())

# Task: auto-send memes
@tasks.loop(seconds=1)
async def auto_meme():
    channel_id = int(os.getenv("CHANNEL_ID"))
    channel = bot.get_channel(channel_id)

    if channel is None:
        print("Channel not found")
        return

    download_meme()
    await asyncio.sleep(30)
    await send_meme(channel)

# Event: bot ready
@bot.event
async def on_ready():
    print(f"{bot.user} connected")
    if not auto_meme.is_running():
        auto_meme.start()

# Event: download images from messages and decode PNGs
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    for attachment in message.attachments:
        # Only decode PNGs
        if attachment.filename.lower().endswith(".png"):
            base, ext = os.path.splitext(attachment.filename)
            counter = 1
            save_path = os.path.join(RECEIVED_DIR, attachment.filename)
            while os.path.exists(save_path):
                save_path = os.path.join(RECEIVED_DIR, f"{base}_{counter}{ext}")
                counter += 1

            # Download the image
            await download_image(attachment.url, save_path)
            print(f"Downloaded {save_path} from {message.author}")

            # Decode and decrypt immediately
            try:
                encoded_message = decode(save_path)
                decrypted_message = decrypt_message(encoded_message)
                # Expect format: "NAME: message"
                if ":" in decrypted_message:
                    author, message_text = decrypted_message.split(":", 1)
                    author = author.strip()
                    message_text = message_text.strip()
                else:
                    author = "UNKNOWN"
                    message_text = decrypted_message.strip()

                inbox.msg_coming({"author": author,"filename": attachment.filename,"message": message_text})

                print(f"[{attachment.filename}] Decoded & decrypted message: {decrypted_message}")
                os.remove(save_path)    
            except Exception as e:
                print(f"[{attachment.filename}] Failed to decode/decrypt: {e}")

    await bot.process_commands(message)

bot.run(os.getenv("DISCORD_TOKEN"))
