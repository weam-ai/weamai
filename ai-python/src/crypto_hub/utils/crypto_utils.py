from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from base64 import b64encode,b64decode
from src.logger.default_logger import logger
from dotenv import load_dotenv
import os
from typing import Dict, Any

load_dotenv()

security_key = os.getenv("SECURITY_KEY").encode("utf-8")

class AESDecryptor:
    def __init__(self, base64_key, base64_iv):
        self.key = b64decode(base64_key)
        self.iv = b64decode(base64_iv)

    def decrypt(self, base64_ciphertext):
        ciphertext = b64decode(base64_ciphertext)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        padded_plaintext = cipher.decrypt(ciphertext)
        plaintext = unpad(padded_plaintext, AES.block_size)
        return plaintext.decode('utf-8')

class MessageEncryptor:
    def __init__(self, key):
        if len(key) not in [16, 24, 32]:
            raise ValueError("Encryption Key must be 16, 24, or 32 bytes long")
        # Ensure the key is 16 bytes for AES-128, or 24 bytes for AES-192, or 32 bytes for AES-256
        self.key = key

    def encrypt(self, plaintext):
        try:
            cipher = AES.new(self.key, AES.MODE_ECB) 
            padded_plaintext = pad(plaintext.encode('utf-8'), AES.block_size) 
            ciphertext = cipher.encrypt(padded_plaintext)
            encrypted_text = b64encode(ciphertext).decode('utf-8')
            return encrypted_text
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

class MessageDecryptor:
    def __init__(self, key):
        if len(key) not in [16, 24, 32]:
            raise ValueError("Decryption Key must be 16, 24, or 32 bytes long")
        self.key = key

    def decrypt(self, base64_ciphertext):
        try:
            ciphertext = b64decode(base64_ciphertext)
            cipher = AES.new(self.key, AES.MODE_ECB)
            decrypted_padded = cipher.decrypt(ciphertext)
            plaintext = unpad(decrypted_padded, AES.block_size)
            return plaintext.decode('utf-8')

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise e

class CryptoService:
    def __init__(self):
        key = os.getenv("SECURITY_KEY")
        if not key:
            raise ValueError("Missing SECURITY_KEY in environment variables")

        key_bytes = key.encode("utf-8")

        if len(key_bytes) not in [16, 24, 32]:
            raise ValueError("SECURITY_KEY must be 16, 24, or 32 bytes long")

        self.encryptor = MessageEncryptor(key_bytes)
        self.decryptor = MessageDecryptor(key_bytes)

    def encrypt(self, plaintext: str) -> str:
        return self.encryptor.encrypt(plaintext)

    def decrypt(self, base64_ciphertext: str) -> str:
        return self.decryptor.decrypt(base64_ciphertext)

crypto_service = CryptoService()

def decrypt_dict_data(encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if not encrypted_data:
            logger.warning("⚠️ No data provided for decryption.")
            return {}

        decryptor = MessageDecryptor(security_key)
        decrypted = {}
        for k, v in encrypted_data.items():
            if isinstance(v, str):
                try:
                    decrypted[k] = decryptor.decrypt(v)
                except Exception as e:
                    logger.warning(f"⚠️ Decryption failed for key '{k}': {e}")
                    decrypted[k] = v
            else:
                decrypted[k] = v

        return decrypted

    except Exception as e:
        logger.exception(f"❌ Unexpected error during dictionary decryption: {e}")
        return {}