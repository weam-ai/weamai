class ToolChatConfig:
    MAX_TOKEN_LIMIT = 10000
    VISION_MODELS = {'gemini-2.0-flash':True, 'gemini-2.5-pro-preview-05-06':True, 'gemini-2.5-flash-preview-04-17':True}
    TEMPRATURE = 0.7
    DEFAUL_GEMINI_1_5_Flash = 'gemini-2.0-flash'

class ImageGenerateConfig:
    MAX_TOKEN_LIMIT = 10000
    LLM_MODEL_NAME = 'gpt-3.5-turbo'
    GPT_4o_MINI = 'gpt-4.1-mini'
    LLM_IMAGE_MODEL = 'dall-e-3'
    DALLE_WRAPPER_SIZE = "1024x1024"
    DALLE_WRAPPER_QUALITY = 'standard'
    n = 1
