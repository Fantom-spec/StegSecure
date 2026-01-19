import os
import secrets
import hashlib
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

load_dotenv()

# --- Load or fail TRUST_KEY ---
trust_key = os.getenv("TRUST_KEY")
if not trust_key:
    raise ValueError("TRUST_KEY not set in .env")

trust_key_bytes = bytes.fromhex(trust_key)

# --- Derive deterministic AES key ---
encryption_key = hashlib.scrypt(
    password=trust_key_bytes,
    salt=b"static_salt_v1",
    n=2**14,
    r=8,
    p=1,
    dklen=32
)

def encrypt_message(message: str) -> bytes:
    aesgcm = AESGCM(encryption_key)
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, message.encode(), None)
    return nonce + ciphertext

def decrypt_message(encrypted_data: bytes) -> str:
    aesgcm = AESGCM(encryption_key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
