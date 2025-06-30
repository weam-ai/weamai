class BaseConfig:
    # Common URLs
    TOOL_CHAT_URL = "/api/tool/stream-tool-chat-with-openai"
    VECTOR_STORE_URL = "/api/vector/openai-store-vector"
    SCRAPPER_URL = "/api/scrape/scrape-url"
    CHAT_WITH_DOC_URL = "/api/chat/streaming-chat-with-doc"
    TITLE_URL = "/api/title/title-chat-generate"
    CUSTOM_GPT_URL = "/api/chat/streaming-custom-gpt-chat-with-doc"
    
    JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY2ZTI4OTJmYTA3NGQyZTVmYzZiYWI3ZCIsImVtYWlsIjoiZGhydXZpc2hwYXRlbEB0YXNrbWUuYml6IiwiaWF0IjoxNzM1ODgyNTk5LCJleHAiOjE3MzU5Njg5OTl9.znuwFTNYH-fS8gJ_KD69kPEc0AGsQ9cGTQJOkeGlJvo"
    # @classmethod
    # def get_url(cls, endpoint):
    #     return getattr(cls, f"{endpoint}_URL", None)


class Local(BaseConfig):
    HOST = "http://0.0.0.0:9000"
    ORIGIN = "0.0.0.0:9000"


class Dev(BaseConfig):
    HOST = "https://dev-pyapi.weam.ai"
    ORIGIN = "https://dev-pyapi.weam.ai"

class Qa(BaseConfig):
    HOST = "https://qa-pyapi.weam.ai"
    ORIGIN = "https://qa-pyapi.weam.ai"

class Prod(BaseConfig):
    HOST = "https://pyapi.weam.ai"
    ORIGIN = "https://app.weam.ai"


class DevPayload:
    TOOL_CHAT = {
        "thread_id": "6777782ed7f134aebef46284",
        "query": "Hiii",
        "prompt_id": None,
        "llm_apikey": "66ff8e48882d3a6413037e4f",
        "chat_session_id": "6777776902295466deef19fb",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02,
        "code": "OPEN_AI",
        "model_name": "gpt-4o"
    }

    TOOL_CHAT_IMG = {
        "thread_id": "67777bd45a8040ab0298d975",
        "query": "Generate image of playing basketball in the largest ground of the world",
        "prompt_id": None,
        "llm_apikey": "66ff8e48882d3a6413037e4f",
        "chat_session_id": "67777bc61d27725ca4b093a0",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02,
        "code": "OPEN_AI",
        "model_name": "gpt-4o"
    }
    
    VECTOR_STORE = {
    "file_type": "pdf",
    "source": "s3_url",
    "file_url": "/documents/674407ac7fe4eabd7f7ab5b0.pdf",
    "page_wise": "False",
    "vector_index": "66e1244ba6344e751faf730c",
    "dimensions": 1536,
    "id": "674407ac7fe4eabd7f7ab5b1",
    "api_key_id": "66ff8e48882d3a6413037e54",
    "tag": "674407ac7fe4eabd7f7ab5b0.pdf",
    "company_id": "66e1244ba6344e751faf730c",
    "brain_id": "66e12eeea6344e751faf7aac"
    }
    
    
    SCRAPPER = {
        "url": "https://example.com",
        "parameters": {
            "param1": "value1",
            "param2": "value2"
        }
    }
    
    CHAT_WITH_DOC = {
        "thread_id": "66f13962036f40815a44bd3d",
        "query": "what is AIRAWAT (AI research, analytics and knowledge assimilation platform)?",
        "llm_apikey": "66f12266036f40815a44bb4d",
        "chat_session_id": "66f13932036f40815a44bd05",
        "file_id": "66f1393e036f40815a44bd35",
        "tag": "66f1393d036f40815a44bd26.pdf",
        "embedding_api_key": "66f12266036f40815a44bb54",
        "brain_id": "66e2c149299e54a706613871",
        "companypinecone": "companypinecone",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02
    }
    
    TITLE = {
        "title": "",
        "thread_id": "66f13897036f40815a44bce3",
        "llm_apikey": "66f12266036f40815a44bb4d",
        "chat_session_id": "66f13879036f40815a44bcb7"
    }
    
    CUSTOM_GPT_WITH_DOC = {
        "thread_id": "66f138ef036f40815a44bcfe",
        "query": "What is The High Catch?",
        "custom_gpt_id": "66f137de036f40815a44bc6a",
        "llm_apikey": "66f12266036f40815a44bb4d",
        "chat_session_id": "66f13879036f40815a44bcb7",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02
    }
    CUSTOM_GPT = {
        "thread_id": "66ed196c1bffa050100cbd9f",
        "query": "What is The Skim Catch?",
        "custom_gpt_id": "66ed18fb1bffa050100cbd36",
        "llm_apikey": "66e2dbe9c217ba8ac4c47aa3",
        "chat_session_id": "66ed19321bffa050100cbd4b",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02
    }

class ProdPayload:
    TOOL_CHAT = {
        "thread_id": "67348b2f645567d38b965eee",
        "query": "Hello",
        "llm_apikey": "66fe416bb08qqq21224bc3eb",
        "chat_session_id": "67348b22147eafd33c6701ed",
        "company_id": "66f3adacd15c34b84ee9dddd",
        "delay_chunk": 0.02
    }
    
    VECTOR_STORE = {
        "file_type": "pdf",
        "source": "s3_url",
        "file_url": "/documents/66ebc0cf2bc16fb0269fb3ba.pdf",
        "page_wise": "False",
        "vector_index": "66e1244ba6344e751faf730c",
        "dimensions": 1536,
        "id": "66ebc0d02bc16fb0269fb3c8",
        "api_key_id": "66e2dbe9c217ba8ac4c47a9f",
        "tag": "66ebc0cf2bc16fb0269fb3ba.pdf",
        "company_id": "66e1244ba6344e751faf730c",
        "brain_id": "66e9255433c996ca463d7b4f"
    }
    
    SCRAPPER = {
        "url": "https://example.com",
        "parameters": {
            "param1": "value1",
            "param2": "value2"
        }
    }
    
    CHAT_WITH_DOC = {
        "thread_id": "66ebf0b42bc16fb0269fb9e5",
        "query": "tell me about this doc",
        "llm_apikey": "66e2dbe9c217ba8ac4c47aa3",
        "chat_session_id": "66ebdbf52bc16fb0269fb737",
        "file_id": "66ebf09d2bc16fb0269fb9dd",
        "tag": "66ebf0982bc16fb0269fb9cf.pdf",
        "embedding_api_key": "66e2dbe9c217ba8ac4c47a9f",
        "brain_id": "66e2c149299e54a706613871",
        "companypinecone": "companypinecone",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02
    }
    
    TITLE = {
        "title": "",
        "thread_id": "66ebf0b42bc16fb0269fb9e5",
        "llm_apikey": "66e2dbe9c217ba8ac4c47aa3",
        "chat_session_id": "66ebdbf52bc16fb0269fb737"
    }
    
    CUSTOM_GPT_WITH_DOC = {
        "thread_id": "66ebfe552bc16fb0269fc199",
        "query": "tell me about this custom bot",
        "custom_gpt_id": "66e7be716f6305ca9497b455",
        "llm_apikey": "66e41f4a06a85108802dea8e",
        "chat_session_id": "66ea64edec2a7f1787bdda25",
        "company_id": "66e02602315ebea9c6487865",
        "delay_chunk": 0.02
    }
    CUSTOM_GPT = {
        "thread_id": "66ed196c1bffa050100cbd9f",
        "query": "What is The Skim Catch?",
        "custom_gpt_id": "66ed18fb1bffa050100cbd36",
        "llm_apikey": "66e2dbe9c217ba8ac4c47aa3",
        "chat_session_id": "66ed19321bffa050100cbd4b",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02
    }

class LocalPayload:
    VECTOR_STORE = {
        "file_type": "pdf",
        "source": "s3_url",
        "file_url": "/documents/673da0ec3302b8d5c6fc5d28.pdf",
        "page_wise": "False",
        "vector_index": "66e1244ba6344e751faf730c",
        "dimensions": 1536,
        "id": "673da0f13302b8d5c6fc5d37",
        "api_key_id": "66ff8e48882d3a6413037e54",
        "tag": "673da0ec3302b8d5c6fc5d28.pdf",
        "company_id": "66e1244ba6344e751faf730c",
        "brain_id": "67343aae974f670346df56e0"
    }

    TOOL_CHAT_IMG = {
        "thread_id": "67777bd45a8040ab0298d975",
        "query": "Generate image of playing basketball in the largest ground of the world",
        "prompt_id": None,
        "llm_apikey": "66ff8e48882d3a6413037e4f",
        "chat_session_id": "67777bc61d27725ca4b093a0",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02,
        "code": "OPEN_AI",
        "model_name": "gpt-4o"
    }
class QaPayload:
    VECTOR_STORE = {
    "file_type": "pdf",
    "source": "s3_url",
    "file_url": "/documents/673dc6ab0f861861a563d8b9.pdf",
    "page_wise": "False",
    "vector_index": "66e042e43dde18ff99b078e9",
    "dimensions": 1536,
    "id": "673dc6ad0f861861a563d8c8",
    "api_key_id": "66fbac20866cbac15467df13",
    "tag": "673dc6ab0f861861a563d8b9.pdf",
    "company_id": "66e042e43dde18ff99b078e9",
    "brain_id": "66e12a503dde18ff99b0845f"
    }
        
    TOOL_CHAT = {
        "thread_id": "67777a10788688e723ed34a5",
        "query": "Hello",
        "prompt_id": None,
        "llm_apikey": "676ab8f1102203724e62636a",
        "chat_session_id": "67777a03788688e723ed3475",
        "company_id": "676ab8e3102203724e62633d",
        "delay_chunk": 0.02,
        "code": "OPEN_AI",
        "model_name": "gpt-4o"
    }
    TOOL_CHAT_IMAGE = {
        "thread_id": "67777bd45a8040ab0298d975",
        "query": "Generate image of playing basketball in the largest ground of the world",
        "prompt_id": None,
        "llm_apikey": "66ff8e48882d3a6413037e4f",
        "chat_session_id": "67777bc61d27725ca4b093a0",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02,
        "code": "OPEN_AI",
        "model_name": "gpt-4o"
    }