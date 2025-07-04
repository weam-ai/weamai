from src.crypto_hub.repositories.openai.llm_model_repo import LLMModelRepository
from src.logger.default_logger import logger
from src.crypto_hub.utils.crypto_utils import crypto_service
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance

llm_model_repo = LLMModelRepository()

load_dotenv()

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
    def initialization(self, api_key_id, collection_name):
        try:
            self.repository = llm_model_repo.initialization(api_key_id, collection_name)
            self.__encrypted_data = llm_model_repo._get_config_data()
            self.cred_config=self.__encrypted_data
            self.model_name = llm_model_repo.get_model_name()
            self.bot_data = llm_model_repo.get_bot_data()
            self.extra_config = llm_model_repo.get_extra_config()
            self.api_key_id=api_key_id
            self.instance = db_instance.get_collection(collection_name)
            self.endpoint_url=self.__encrypted_data['endpoint']
            self.custom_headers=self.cred_config.get("headers", None)
            self.task_type=self.__encrypted_data['taskType']
            self.tool_call=llm_model_repo.tool_enable()
            self.vision_enable=llm_model_repo.vision_enable()
            self.streaming = llm_model_repo.stream_enable()
            self.repo = self.__encrypted_data['repo']

            if self.__encrypted_data:
                self.apikey = self.__encrypted_data.get('apikey')

                if not crypto_service:
                    logger.error(
                        "crypto_service is not enable. Please ensure that the crypto_service is properly set.",
                        extra={"tags": {
                            "method": "LLMAPIKeyDecryptionHandler.initialization",
                            "api_id": api_key_id
                        }})
                    raise ValueError("Crypto service is not rechable. Please ensure that the crypto_service is properly set.")
                self.decryptor = crypto_service.decryptor
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