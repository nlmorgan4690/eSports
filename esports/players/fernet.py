from cryptography.fernet import Fernet
from flask import current_app

def get_fernet():
    key = current_app.config['FERNET_KEY']
    return Fernet(key)

def encrypt_string(plaintext):
    return get_fernet().encrypt(plaintext.encode()).decode()

def decrypt_string(ciphertext):
    return get_fernet().decrypt(ciphertext.encode()).decode()
