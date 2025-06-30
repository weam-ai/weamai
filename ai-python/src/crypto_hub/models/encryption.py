import base64

class EncryptionConfig:
    """
    Configuration class for storing and handling cryptographic keys and IVs.

    Attributes:
        key (str): Base64-encoded cryptographic key.
        iv (str): Base64-encoded initialization vector.
        algorithm (str): The encryption algorithm to be used.
    """
    def __init__(self, base64_key, base64_iv, algorithm):
        # Validate that the key, IV, and algorithm are not empty
        if not base64_key or not base64_iv or not algorithm:
            raise ValueError("Key, IV, and algorithm cannot be empty.")

        # Validate that the key and IV are base64-encoded
        if not (self.is_base64(base64_key) and self.is_base64(base64_iv)):
            raise ValueError("Key and IV must be base64-encoded strings")

        self.key = base64_key
        self.iv = base64_iv
        self.algorithm = algorithm

    @staticmethod
    def is_base64(s):
        """Check if the provided string s is base64 encoded."""
        try:
            base64.b64decode(s)
            return True
        except ValueError:
            return False
