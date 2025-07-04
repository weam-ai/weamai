from src.crypto_hub.repositories.openai.embedding_model_repo import EmbeddingModelRepository
from src.logger.default_logger import logger
from dotenv import load_dotenv
import os
from src.crypto_hub.utils.crypto_utils import crypto_service

load_dotenv()

embedding_model_repo = EmbeddingModelRepository()


class EmbeddingAPIKeyDecryptionHandler:
    """
    Class to handle the decryption of data using API key-specific configurations.

    Attributes:
        repository (EmbeddingAPIKeyDecryptionHandler): The repository to fetch company model data.
        __encrypted_data (dict): The encrypted configuration data.
        model_name (str): The model name fetched from the repository.
        dimensions (dict): The dimensions fetched from the repository.
        algorithm (str): The encryption algorithm used (default is 'AES').
        key (str): The encryption key.
        iv (str): The initialization vector.
        decryptor (object): The decryptor instance for the specified algorithm.
    """

    def initialization(self, api_key_id, collection_name):
        """
        Initializes the DecryptionAPIKey with the given API key identifier.

        Args:
            api_key_id (str): The API key identifier.

        Raises:
            ValueError: If no encrypted data is found or if the algorithm is unsupported.
        """
        try:
            self.repository = embedding_model_repo.initialization(api_key_id, collection_name)
            self.__encrypted_data = embedding_model_repo._get_config_data()
            self.model_name = embedding_model_repo.get_model_name()
            self.dimensions = embedding_model_repo.get_dimensions()

            if self.__encrypted_data:
                self.apikey = self.__encrypted_data.get('apikey')

                if not crypto_service:
                    logger.error(
                        "crypto_service is not enable. Please ensure that the crypto_service is properly set.",
                        extra={"tags": {
                            "method": "EmbeddingAPIKeyDecryptionHandler.initialization",
                            "api_id": api_key_id
                        }})
                    raise ValueError("Crypto service is not rechable. Please ensure that the crypto_service is properly set.")
                self.decryptor = crypto_service.decryptor
            else:
                logger.error(
                    f"No encrypted data found for API key ID: {api_key_id}",
                    extra={"tags": {
                        "method": "EmbeddingAPIKeyDecryptionHandler.initialization",
                        "api_id": api_key_id
                    }}
                )
                raise ValueError("No encrypted data found for the given API key ID")
            logger.info(
                f"Embedding Decrypt class successfully initiated",
                extra={"tags": {
                    "method": "EmbeddingAPIKeyDecryptionHandler.initialization",
                    "api_id": api_key_id
                }}
            )
        except ValueError as e:
            logger.error(
                f"Value error: {e}",
                extra={"tags": {
                    "method": "EmbeddingAPIKeyDecryptionHandler.initialization",
                    "api_id": api_key_id
                }}
            )

    def decrypt(self):
        try:
            if not self.decryptor:
                logger.error(
                    "Decryptor not properly initialized",
                    extra={"tags": {"method": "EmbeddingAPIKeyDecryptionHandler.decrypt"}})
                raise ValueError("Decryptor not properly initialized")
            return self.decryptor.decrypt(self.apikey)
        except ValueError as e:
            logger.error(
                f"Value error: {e}",
                extra={"tags": {"method": "EmbeddingAPIKeyDecryptionHandler.decrypt"}}
            )
