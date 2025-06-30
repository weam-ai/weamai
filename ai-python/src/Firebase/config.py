from src.db.config import get_field_by_name, get_decrypted_details
from typing import Dict, Any
from src.crypto_hub.utils.crypto_utils import decrypt_dict_data, decrypt_dict_data

class FirebaseConfig:
    FIREBASE_CREDENTIALS = get_field_by_name('setting', 'FIREBASE_PRIVATE_KEY', 'details')
