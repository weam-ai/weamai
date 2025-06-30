def generate_unique_number(text: str) -> int:
    """
    Generate a unique SHA-256 hash for the given text.
    
    Args:
        text (str): The input text to hash.
    
    Returns:
        int: The generated unique hash.
    """
    hash_object = hashlib.sha256()
    hash_object.update(text.encode('utf-8'))
    return hash_object.hexdigest()

import hashlib