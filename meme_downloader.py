import requests
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

MEME_DIR = os.getenv("MEME_DIR")
os.makedirs(MEME_DIR, exist_ok=True)

# Allowed image extensions
ALLOWED_EXTS = ['.png', '.jpg', '.jpeg', '.gif', '.webp']

def download_meme():
    while True:
        try:
            r = requests.get("https://meme-api.com/gimme", timeout=5)
            print("API status:", r.status_code)

            data = r.json()
            image_url = data["url"]
            print("Image URL:", image_url)

            # Check extension
            ext = os.path.splitext(image_url)[1].lower()
            if ext not in ALLOWED_EXTS:
                print(f"Not an allowed image type ({ext}), skipping")
                continue

            # Generate unique filename
            filename = f"{uuid.uuid4()}{ext}"
            filepath = os.path.join(MEME_DIR, filename)

            # Download and save image
            img = requests.get(image_url, timeout=10).content
            with open(filepath, "wb") as f:
                f.write(img)

            print("Saved meme:", filepath)
            return filepath

        except Exception as e:
            print("Download failed:", e)
