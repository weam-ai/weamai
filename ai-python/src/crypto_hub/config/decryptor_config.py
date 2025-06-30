from src.crypto_hub.utils.crypto_utils import AESDecryptor  # Import specific decryptors

# Dictionary mapping algorithm names to their corresponding decryptor classes
DECRYPTOR_CLASSES = {
    'AES': AESDecryptor,
    # 'DES': DESDecryptor,  # Add additional decryptors as needed
}
