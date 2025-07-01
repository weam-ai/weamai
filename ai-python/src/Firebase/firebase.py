import firebase_admin
from firebase_admin import credentials, messaging
from src.Firebase.config import FirebaseConfig
from src.logger.default_logger import logger
from src.db.config import get_field_by_name, get_decrypted_details

name_value = get_field_by_name('setting', 'FIREBASE_PRIVATE_KEY', 'details')

class Firebase:
    def __init__(self):
        self.app = None
        self.initialized = False
        if FirebaseConfig.FIREBASE_CREDENTIALS:
            self.cred = credentials.Certificate(FirebaseConfig.FIREBASE_CREDENTIALS)
            self.app = firebase_admin.initialize_app(self.cred)
            self.initialized=True
        
    def send_push_notification(self, tokens: list, title: str, body: str=None):
        if not self.initialized:
            logger.info("send_push_notification called, but Firebase is not initialized.")
            return None  # Or return a dummy respon
        else:
            messages = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                tokens=tokens,
            )
            response = messaging.send_each_for_multicast(messages)
            return response

firebase = Firebase()
