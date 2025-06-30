from bson.objectid import ObjectId
from src.chatflow_langchain.service.config.baseModel_repository import BaseDefaultModelRepository
from src.logger.default_logger import logger
from src.crypto_hub.utils.crypto_utils import MessageEncryptor,MessageDecryptor
from dotenv import load_dotenv
import os
load_dotenv()

key = os.getenv("SECURITY_KEY").encode("utf-8")

encryptor = MessageEncryptor(key)
decryptor = MessageDecryptor(key)
class GEMINIMODEL:
    GEMINI_2O_FLASH= 'gemini-2.0-flash'
    DEFAULT_TOOL_MODEL = 'gemini-2.0-flash'
    VISION_MODELS = {'gemini-2.0-flash':True, 'gemini-2.5-pro-preview-05-06':True, 'gemini-2.5-flash-preview-04-17':True}

class Functionality:
    CHAT = 'CHAT'
    AGENT = 'AGENT'
    
class DefaultGEMINI20FlashModelRepository(BaseDefaultModelRepository):
    def get_default_model_key(self):
        query = {
            "name": GEMINIMODEL.GEMINI_2O_FLASH,
            "company.id": ObjectId(self.company_id)
        }
        projection = {'_id': 1}
        return super().get_default_model_key(query, projection)
    def get_encrypt_key(self) -> str:
        """
        Decrypt the provided key using the company's encryption method.


        Returns:
            str: The decrypted key.
        """
        query = {
            "name": GEMINIMODEL.GEMINI_2O_FLASH,
            "company.id": ObjectId(self.company_id)
        }
        projection = {'config.apikey': 1}

        self.response = self.get_collection().find_one(query, projection)
         
        # Placeholder for decryption logic
        self.encrypt_key=self.response.get("config","").get("apikey","")
        # Replace with actual decryption code
        return self.encrypt_key
    def get_decrypt_key(self) -> str:
        """
        Decrypt the encrypted key retrieved from the database.

        This method uses the decryptor to decrypt the encrypted key 
        fetched from the database for the specified company and model.

        Returns:
            str: The decrypted key.
        """
      
        
        try:
            decrypted_key = decryptor.decrypt(self.encrypt_key)
            return decrypted_key
        except Exception as e:
            logger.error(f"Failed to decrypt the key for company id {self.company_id}: {e}")

class DefaultGeminiModelRepository(BaseDefaultModelRepository):
    def get_default_model_key(self):
        query = {
            "name": GEMINIMODEL.GEMINI_2O_FLASH,
            "company.id": ObjectId(self.company_id)
        }
        projection = {'_id': 1}
        return super().get_default_model_key(query, projection)