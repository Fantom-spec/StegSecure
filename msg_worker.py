import os
import time
from dotenv import load_dotenv
from crypto import encrypt_message
from steganography import encode

load_dotenv()

MEME_DIR = os.getenv("MEME_DIR")
if not MEME_DIR:
    raise ValueError("MEME_DIR not set")

QUEUE_FILE = "message_queue.txt"
PROCESSED_FILE = "processed_images.txt"

# --- Load processed images ---
processed = set()
if os.path.exists(PROCESSED_FILE):
    with open(PROCESSED_FILE, "r") as f:
        processed = set(line.strip() for line in f)

# --- Queue helper ---
def read_next_message():
    if not os.path.exists(QUEUE_FILE):
        return None
    with open(QUEUE_FILE, "r") as f:
        lines = f.readlines()
    if not lines:
        return None
    msg = lines[0].strip().replace("\n", " ")
    # remove after read
    with open(QUEUE_FILE, "w") as f:
        f.writelines(lines[1:])
    return msg

print("[*] msg_worker started")

# --- Main loop ---
while True:
    try:
        files = [f for f in os.listdir(MEME_DIR) if f.lower().endswith(".png")]
        new_files = [f for f in files if f not in processed]

        for file_name in new_files:
            message = read_next_message()
            if not message:
                break  # queue empty

            img_path = os.path.join(MEME_DIR, file_name)
            out_path = os.path.join(MEME_DIR, f"enc_{file_name}")

            try:
                encrypted_bytes = encrypt_message(message)
                encode(img_path, img_path, encrypted_bytes)
                print(f"[+] Embedded encrypted message into {file_name}")
                processed.add(file_name)
                with open(PROCESSED_FILE, "a") as pf:
                    pf.write(file_name + "\n")
            except Exception as e:
                print(f"[!] Encode failed for {file_name}: {e}")

        time.sleep(2)
    except Exception as e:
        print(f"[!] Worker error: {e}")
        time.sleep(2)
