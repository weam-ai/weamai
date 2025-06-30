from src.crypto_hub.models.encryption import EncryptionConfig
from src.db.config import db_instance
from src.logger.default_logger import logger

class CryptoRepository:
    def __init__(self):
        # The db_instance is assumed to be a pre-configured and connected MongoDB database instance.
        self.encryption_configs = db_instance.encryption_configs

    def get_encryption_data(self, company_id, description):
        """Retrieve encryption configuration and ciphertext based on company ID and description."""
        return self._get_data(company_id, description)

    def get_openai_key(self, company_id):
        """Retrieve OpenAI API key based on company ID."""
        return self._get_data(company_id, 'openai_api')

    def get_google_bard_key(self, company_id):
        """Retrieve Google Bard API key based on company ID."""
        return self._get_data(company_id, 'google_bard_api')

    def _get_data(self, company_id, description):
        """Generic method to retrieve data based on company ID and description."""
        try:
            query = {'company_id': company_id, 'description': description}
            config_data = self.encryption_configs.find_one(query)
            if config_data:
                if 'key' in config_data and 'iv' in config_data and 'algorithm' in config_data:
                    encryption_config = EncryptionConfig(config_data['key'], config_data['iv'], config_data['algorithm'])
                    ciphertext = config_data.get('ciphertext', None)
                    return encryption_config, ciphertext
                else:
                    return config_data.get('key'), None  # Assuming only the key is needed for API configurations
            else:
                return None, None
        except Exception as e:
            logger.error(
                f"An error occurred while retrieving data for company_id: {company_id}, description: {description}: {e}",
                extra={"tags": {"method": "CryptoRepository._get_data"}}
            )
            return None, None
