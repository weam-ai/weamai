# import os
# from dotenv import load_dotenv

# class EnvConfig:
#     """Centralized environment configuration with direct attribute access."""

#     # Load environment variables once
#     load_dotenv()

#     # Define and store environment variables as class attributes
#     API_CALL_COUNT_KEY_REDIS = os.getenv("API_CALL_COUNT_KEY_REDIS", "redis_api_call_count")
#     REDIS_URL = os.getenv("CELERY_BROKEN_URL")
#     CELERY_BROKER_URL = os.getenv("CELERY_BROKEN_URL")
#     CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
#     SCHEDULER_TIME = int(os.getenv("SCHEDULER_TIME", 50))
#     DEFAULT_CELERY_TASK_EXP = int(os.getenv("DEFAULT_CELERY_TASK_EXP", 86400))
#     CELERY_TASK_ALWAYS_EAGER = str(os.getenv("CELERY_TASK_ALWAYS_EAGER", "false")).lower() in ("true", "1", "yes")

#     @classmethod
#     def get(cls, key, default=None):
#         """Dynamically fetch a configuration value."""
#         return getattr(cls, key, default)


import os
from src.logger.default_logger import logger    
import time
from dotenv import load_dotenv

class EnvConfig:
    """Centralized environment configuration loader with logging."""

    _is_loaded = False  # Ensures env variables are loaded only once

    @classmethod
    def _load_env(cls):
        """Loads environment variables only once when the class is first accessed."""
        if not cls._is_loaded:
            start_time = time.time()  # Start tracing time

            logger.info("Loading environment variables...")

            load_dotenv()  # Load .env file once

            # Define environment variables as class attributes (accessible globally)
            cls.API_CALL_COUNT_KEY_REDIS = os.getenv("API_CALL_COUNT_KEY_REDIS", "redis_api_call_count")
            cls.REDIS_URL = os.getenv("CELERY_BROKEN_URL", "redis://localhost:6379/0")
            cls.CELERY_BROKER_URL = os.getenv("CELERY_BROKEN_URL", "redis://localhost:6379/0")
            cls.CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
            cls.SCHEDULER_TIME = int(os.getenv("SCHEDULER_TIME", 50))
            cls.DEFAULT_CELERY_TASK_EXP = int(os.getenv("DEFAULT_CELERY_TASK_EXP", 86400))
            cls.CELERY_TASK_ALWAYS_EAGER = str(os.getenv("CELERY_TASK_ALWAYS_EAGER", "false")).lower() in ("true", "1", "yes")

            elapsed_time = time.time() - start_time  # Measure elapsed time

            logger.info(f"Environment variables loaded successfully in {elapsed_time:.4f} seconds")
            cls._is_loaded = True  # Prevent reloading

    @classmethod
    def get(cls, key, default=None):
        """Dynamically fetch a configuration value with a default fallback."""
        value = getattr(cls, key, os.getenv(key, default))  # Get attribute or environment value
        logger.debug(f"Accessing config: {key} = {value}")
        return value

# Load environment variables once when the class is first imported
EnvConfig._load_env()

