class ToolChatConfig:
    MAX_TOKEN_LIMIT = 8096
    VISION_MODELS = {'gpt-4o': True, 'gpt-4.1-mini': True, 'gpt-4-turbo': True}
    TEMPRATURE = 0.7
    DEFAULT_GPT_4o_MINI = 'gpt-4.1-mini'
    HUGGINGFACE_HISTORY_OFFSET=1500,
    THREAD_COLLECTION="messages"
    MAX_TOTAL_TOKENS = 4096


class ImageGenerateConfig:
    MAX_TOKEN_LIMIT = 10000
    LLM_MODEL_NAME = 'gpt-3.5-turbo'
    GPT_4o_MINI = 'gpt-4.1-mini'
    LLM_IMAGE_MODEL = 'dall-e-3'
    DALLE_WRAPPER_SIZE = "1024x1024"
    DALLE_WRAPPER_QUALITY = 'standard'
    n = 1
