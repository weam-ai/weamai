class ToolChatConfig:
    MAX_TOKEN_LIMIT = 10000
    VISION_MODELS = {'gpt-4.1': True, 'gpt-4.1-mini': True, 'gpt-4.1-nano': True, 'gpt-4o-2024-11-20':True}
    TEMPRATURE = 0.7
    DEFAULT_GPT_4o_MINI = 'gpt-4.1-mini'
    IMAGE_SIZE_LIST = ["1024x1024","1792x1024","1024x1792"]

class ImageGenerateConfig:
    MAX_TOKEN_LIMIT = 10000
    LLM_MODEL_NAME = 'gpt-3.5-turbo'
    GPT_4o_MINI = 'gpt-4.1-mini'
    LLM_IMAGE_MODEL = 'dall-e-3'
    DALLE_WRAPPER_SIZE = "1024x1024"
    DALLE_WRAPPER_QUALITY = 'standard'
    n = 1
