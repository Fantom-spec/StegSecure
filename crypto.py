import os
import secrets
import hashlib
from dotenv import load_dotenv, set_key
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ENV_FILE = ".env"

# Load env
load_dotenv(ENV_FILE)

trust_key = os.getenv("TRUST_KEY")

# ---- Generate TRUST_KEY if missing ----
if not trust_key:
    trust_key = secrets.token_hex(16)  # 16 bytes = 128 bits
    set_key(ENV_FILE, "TRUST_KEY", trust_key)
    print(f"[+] Generated TRUST_KEY and saved to .env:\n{trust_key}")

trust_key_bytes = bytes.fromhex(trust_key)

# ---- Derive encryption key (deterministic) ----
encryption_key = hashlib.scrypt(
    password=trust_key_bytes,
    salt=b"static_salt_v1",   # constant salt is OK since trust_key is high entropy
    n=2**14,
    r=8,
    p=1,
    dklen=32                 # 32 bytes = AES-256
)

# ---- Encrypt ----
def encrypt_message(message: str) -> bytes:
    aesgcm = AESGCM(encryption_key)
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, message.encode(), None)
    return nonce + ciphertext

# ---- Decrypt ----
def decrypt_message(encrypted_data: bytes) -> str:
    aesgcm = AESGCM(encryption_key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()

# ---- Demo ----
# if __name__ == "__main__":
    #msg = "persistent secret message"
    #print(encryption_key.hex())

    #encrypted = encrypt_message(msg)
    #print("\nEncrypted (hex):", encrypted.hex())

    # decrypted = decrypt_message(bytes.fromhex('a57676a70785bd08ede07aec77587d4a25e4eeb84deb35d14dee7512dc018c832c'))
    # print("Decrypted:", decrypted)
