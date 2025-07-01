import hashlib
def hash_website(website):
    encoded_string= website.encode()
    sha256_hash = hashlib.sha256()
    
        # Update the hash object with the encoded string
    sha256_hash.update(encoded_string)

    # Get the hexadecimal representation of the hash
    hash_output=sha256_hash.hexdigest()
    return hash_output