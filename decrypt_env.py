import os
from cryptography.fernet import Fernet

key = os.environ.get("ENCRYPTION_KEY")
if not key:
    raise ValueError("ENCRYPTION_KEY not set")

fernet = Fernet(key)

with open(".env.enc", "rb") as enc_file:
    decrypted = fernet.decrypt(enc_file.read())

with open(".env", "wb") as dec_file:
    dec_file.write(decrypted)

print("✅ .env decrypted")
