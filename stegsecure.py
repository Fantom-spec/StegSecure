import click
import secrets
import subprocess
from dotenv import load_dotenv, set_key
from msg_sender import send_message
import os
import signal
import time
from inbox import msg_sending

PID_FILE = "bot.pid"

load_dotenv()

@click.group()
def main():
    pass

@main.command()
@click.option("--value", "-v",help="Provide TRUST_KEY manually (optional)")
def trust_key(value):
    if value:
        key = value
    else:
        key = secrets.token_hex(16)
    set_key(".env", "TRUST_KEY", key)

@main.command()
@click.argument("text")
def name(text):
    set_key(".env","NAME",text)

@main.command()
def inbox():
    msg_sending()

@main.command()
def status():
        click.echo("Name: ")
        click.echo("Bot Configured: ")
        click.echo("Bot Status: ")

@main.command()
@click.argument("text")
def send(text):
    send_message(text)

@main.command()
def bot_start():
    if os.path.exists(PID_FILE):
        print("Bot already running.")
        return
    
    proc = subprocess.Popen(
        ["python", "bot.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))

    print(f"Bot started with PID {proc.pid}")

@main.command()
def bot_stop():
    if not os.path.exists(PID_FILE):
        print("Bot is not running.")
        return

    with open(PID_FILE, "r") as f:
        pid = int(f.read())

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Bot stopped (PID {pid})")
    except ProcessLookupError:
        print("Process not found. Cleaning up PID file.")
    finally:
        os.remove(PID_FILE)


@main.command()
@click.option("--discord-token", "-dt",prompt="Enter Discord bot token",hide_input=True,help="Discord bot token")
@click.option("--channel-id", "-cd",type=int,prompt="Enter Discord channel ID",help="Discord channel ID (integer only)")
def bot_init(discord_token, channel_id):
    set_key(".env","DISCORD_TOKEN",discord_token)
    set_key(".env","CHANNEL_ID",str(channel_id))

if __name__ == "__main__":
    main()
