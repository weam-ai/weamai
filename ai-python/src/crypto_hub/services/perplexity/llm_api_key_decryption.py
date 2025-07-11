from src.crypto_hub.repositories.openai.llm_model_repo import LLMModelRepository
from src.logger.default_logger import logger
from src.crypto_hub.utils.crypto_utils import MessageDecryptor
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.round_robin.llm_key_manager import APIKeySelectorService

load_dotenv()
security_key = os.getenv("SECURITY_KEY").encode("utf-8")

llm_model_repo = LLMModelRepository()

class LLMAPIKeyDecryptionHandler:
    """
    Handles decryption of encrypted data using the provided API key ID and collection name.

    Attributes:
        repository: The repository for the LLM model.
        model_name (str): The name of the LLM model.
        extra_config (dict): Extra configuration data for the LLM model.
        algorithm (str): The encryption algorithm used.
        key (bytes): The encryption key.
        iv (bytes): The initialization vector (IV) for encryption.
        ciphertext (bytes): The encrypted data.
        decryptor: The decryptor object based on the specified algorithm.

    Methods:
        initialization(api_key_id: str, collection_name: str) -> None:
            Initializes the decryption handler with the provided API key ID and collection name,
            setting up necessary attributes for decryption.

        decrypt() -> bytes:
            Decrypts the ciphertext using the specified decryptor object and returns the plaintext.

    Raises:
        ValueError: If encryption key or IV is missing, if the algorithm is unsupported, or if no encrypted data is found.
    """
    def initialization(self, api_key_id, collection_name,**kwargs):
        try:
            self.apikey=None
            self.repository = llm_model_repo.initialization(api_key_id, collection_name)
            self.__encrypted_data = llm_model_repo._get_config_data()
            self.model_name = llm_model_repo.get_model_name()
            self.bot_data = llm_model_repo.get_bot_data()
            self.extra_config = llm_model_repo.get_extra_config()
            self.api_key_id=api_key_id
            self.instance = db_instance.get_collection(collection_name)
            self.company_id=str(llm_model_repo.result.get('company',{}).get('id'))
            self.functionality = kwargs.get('functionality', 'CHAT')
            # self.api_key_selector_service = APIKeySelectorService()
            # self.companyKeys = llm_model_repo.get_companyKeys(llm_model_repo.result['company']['id'])  # FOR  ROUND_ROBIN FUTURE USE
            self.companyKeys = False
            self.companyRedis_id = str(llm_model_repo.result['company']['id']) if self.companyKeys else 'default'
            # self.apikey = self.api_key_selector_service.sync_get_best_api_key(provider=self.bot_data.get('code', 'PERPLEXITY'), model=self.model_name, functionality=self.functionality,company_id=self.companyRedis_id)

            if not security_key:
                    logger.error(
                        "Security key is missing in the environment file. Please ensure that the SECURITY_KEY is properly set.",
                        extra={"tags": {
                            "method": "LLMAPIKeyDecryptionHandler.initialization",
                            "api_id": api_key_id
                        }})
                    raise ValueError("Security key is missing in the environment file. Please ensure that the SECURITY_KEY is properly set.")

            self.decryptor = MessageDecryptor(security_key)
            if not self.apikey:
                if self.__encrypted_data:
                    self.apikey = self.__encrypted_data.get('apikey')
                else:
                    logger.error(
                        f"No encrypted data found for API key ID: {api_key_id}",
                        extra={"tags": {
                            "method": "LLMAPIKeyDecryptionHandler.initialization",
                            "api_id": api_key_id
                        }}
                    )
                    raise ValueError("No encrypted data found for the given API key ID")
            logger.info(
                f"LLM Decrypt class successfully initiated",
                extra={"tags": {
                    "method": "LLMAPIKeyDecryptionHandler.initialization",
                    "api_id": api_key_id
                }})
        except ValueError as e:
            logger.error(
                f"Value error: {e}",
                extra={"tags": {
                    "method": "LLMAPIKeyDecryptionHandler.initialization",
                    "api_id": api_key_id
                }})

    def decrypt(self):
        try:
            if not self.decryptor:
                logger.error(
                    "Decryptor not properly initialized",
                    extra={"tags": {"method": "LLMAPIKeyDecryptionHandler.decrypt"}}
                )
                raise ValueError("Decryptor not properly initialized")
            return self.decryptor.decrypt(self.apikey)
        except ValueError as e:
            logger.error(
                f"Value error: {e}",
                extra={"tags": {"method": "LLMAPIKeyDecryptionHandler.decrypt"}}
            )

    def update_deprecated_status(self, is_deprecated: bool):
        """
        Update the is_deprecated status of the thread model.

        Args:
            is_deprecated (bool): The new deprecated status.
        """
        query = {'_id': ObjectId(self.api_key_id)}
        data = {
            "$set": {
                "is_deprecated": is_deprecated
            }
        }
        try:
            self.instance.update_one(query, data)
            logger.info(
                f"Successfully updated is_deprecated status to {is_deprecated} for Llm key ID: {self.api_key_id}",
                extra={"tags": {
                    "method": "LLMAPIKeyDecryptionHandler.update_deprecated_status",
                    "llm_key_id": self.api_key_id
                }}
            )
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the is_deprecated status: {e}",
                extra={"tags": {
                    "method": "LLMAPIKeyDecryptionHandler.update_deprecated_status",
                    "llm_key_id": self.api_key_id
                }}
            )