import subprocess
import sys
import os
from dotenv import load_dotenv

load_dotenv()

QUEUE_FILE = "message_queue.txt"
PID_FILE = "msg_worker.pid"

def is_worker_running():
    if not os.path.exists(PID_FILE):
        return False
    try:
        pid = int(open(PID_FILE).read())
        os.kill(pid, 0)
        return True
    except:
        return False

def start_worker():
    proc = subprocess.Popen(
        [sys.executable, "msg_worker.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))

def send_message(text: str):
    text = text.strip().replace("\n", " ")  # sanitize newlines
    if not text:
        print("[-] Empty message")
        return

    with open(QUEUE_FILE, "a") as f:
        f.write(f"{os.getenv('NAME', 'UNKNOWN')}: {text}\n")

    print(f"[+] {os.getenv('NAME', 'UNKNOWN')}: {text}")

    if not is_worker_running():
        start_worker()
        print("[*] Worker subprocess started")
    
