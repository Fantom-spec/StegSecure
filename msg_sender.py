import os
import time
from dotenv import load_dotenv
from steganography import encode
from queue import Queue
import threading
from crypto import encrypt_message

load_dotenv()

MEME_DIR = os.getenv("MEME_DIR")
if not MEME_DIR:
    raise ValueError("MEME_DIR not set in .env")

message_queue = Queue()
processed_files = set()

# ===== Thread to collect messages =====
def message_input_thread():
    while True:
        msg = input("Enter message to embed: ").strip()
        if msg:
            # No padding, just queue the message
            message_queue.put(msg)
            print(f"Message queued: {msg}")

threading.Thread(target=message_input_thread, daemon=True).start()

# ===== Main loop to watch for new PNGs =====
while True:
    files = [f for f in os.listdir(MEME_DIR) if f.lower().endswith(".png")]
    new_files = [f for f in files if f not in processed_files]

    for file_name in new_files:
        input_path = os.path.join(MEME_DIR, file_name)

        if not os.path.isfile(input_path):
            continue

        if message_queue.empty():
            continue

        secret_message = message_queue.get()
        try:
            # Encrypt message -> get bytes -> convert to hex
            encrypted_bytes = encrypt_message(secret_message)
            hex_message = encrypted_bytes.hex()  # this is what gets embedded
            encode(input_path, input_path, hex_message)
            print(f"Message embedded into {file_name}: '{secret_message}'")
            processed_files.add(file_name)
        except Exception as e:
            print(f"Encoding failed for {file_name}: {e}")

    time.sleep(2)
