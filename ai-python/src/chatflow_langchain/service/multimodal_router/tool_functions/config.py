class ToolChatConfig:
    MAX_TOKEN_LIMIT = 10000
    VISION_MODELS = {'meta-llama/llama-4-maverick:free': True, 'meta-llama/llama-4-maverick': True, 'meta-llama/llama-4-scout:free': True, 'meta-llama/llama-4-scout': True, 'qwen/qwen3-30b-a3b:free': True}
    TEMPRATURE = 0.7
    IMAGE_SIZE_LIST = ["1024x1024","1792x1024","1024x1792"]

class ImageGenerateConfig:
    MAX_TOKEN_LIMIT = 10000
    LLM_IMAGE_MODEL = 'dall-e-3'
    GPT_4o_MINI = 'gpt-4.1-mini'
    DALLE_WRAPPER_SIZE = "1024x1024"
    DALLE_WRAPPER_QUALITY = 'standard'
    n = 1
