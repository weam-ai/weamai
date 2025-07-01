class ToolChatConfig:
    MAX_TOKEN_LIMIT = 10000
    VISION_MODELS = {'gpt-4.1': True, 'gpt-4.1-mini': True, 'gpt-4.1-nano': True, 'gpt-4o-2024-11-20':True, 'chatgpt-4o-latest':True}
    TEMPRATURE = 1
    DEFAULT_GPT_4o_MINI = 'gpt-4.1-mini'
    IMAGE_SIZE_LIST = ["1024x1024","1792x1024","1024x1792","1024x1536","1536x1024"]

class ImageGenerateConfig:
    MAX_TOKEN_LIMIT = 10000
    GPT_4o_MINI = 'gpt-4.1-mini'
    LLM_IMAGE_MODEL = 'gpt-image-1'
    DALLE_WRAPPER_SIZE = "1024x1024"
    DALLE_WRAPPER_QUALITY = 'high'
    n = 1

class WebSearchConfig:
    SEARCH_CONTEXT_SIZE = 'low'
    MODEL_LIST=['gpt-4.1-search-medium']