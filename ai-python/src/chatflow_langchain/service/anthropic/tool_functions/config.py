class ToolChatConfig:
    MAX_TOKEN_LIMIT = 10000
    VISION_MODELS = {
                    'claude-3-5-sonnet-latest': True,
                     'claude-3-5-sonnet-20241022':True,
                     'claude-3-opus-20240229':True,
                     'claude-3-sonnet-20240229':True,
                     'claude-3-haiku-20240307':True,
                     'claude-3-opus-latest':True,
                     'claude-3-7-sonnet-latest':True,
                     'claude-3-5-haiku-latest':True,
                     'claude-opus-4-20250514':True,
                     'claude-sonnet-4-20250514':True
                     }
    TEMPRATURE = 0.7
    DEFAULT_GPT_4o_MINI = 'gpt-4.1-mini'
    DEFAULT_ANTHROPIC_SONNET = 'claude-3-5-sonnet-latest'

class ImageGenerateConfig:
    MAX_TOKEN_LIMIT = 10000
    LLM_MODEL_NAME = 'gpt-3.5-turbo'
    GPT_4o_MINI = 'gpt-4.1-mini'
    LLM_IMAGE_MODEL = 'dall-e-3'
    DALLE_WRAPPER_SIZE = "1024x1024"
    DALLE_WRAPPER_QUALITY = 'standard'
    n = 1
