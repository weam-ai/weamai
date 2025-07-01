class CustomFastapiConfig:
    MAX_TOKEN_LIMIT = 4000
    DELAY_CHUNK = 0.0
    LIMIT_GPT_DOC = "5/minute"

class TestCaseConfig:
    SIMPLE_CHAT_URL = "/api/chat/stream-chat-with-openai"
    STREAM_CHAT_DOC_URL = "/api/chat/streaming-chat-with-doc"
    STREAM_CUSTOM_GPT_CHAT_DOC_URL = "/api/chat/streaming-custom-gpt-chat-with-doc" 
    OPENAI_STORE_VECTOR_URL = "/api/vector/openai-store-vector" 
    TITLE_CHAT_GENERATE_URL = "/api/title/title-chat-generate" 
    SCRAPE_URL = "/api/scrape/scrape-url" 
    TOOL_CHAT_URL = "/api/tool/stream-tool-chat-with-openai"
    CANVAS_CHAT_URL = "/api/canvas/canvas-chat-generate"
    INVALID_VALUE = "12345"
    INVALID_TYPE = 12345
    IMAGE_URL = "/images/667a8518d1c136493ffa3a4f.jpeg"
    INVALID_IMAGE_URL = "/images/667a8518d1c136493ffa3a4f.pdf" # Added .pdf file in url for create invalid image url

    SIMPLE_CHAT_WITH_OPENAI_REQUEST_BODY = {
        "thread_id": "66ab8b04161d8668d79a3b8f",
        "query": "give me a list of 10 basketball players of golden state",
        "llm_apikey": "66a0cf231bd0b30bb78e92be",
        "chat_session_id": "66ab8adc161d8668d79a3b79",
        "company_id": "666fd7cfb950158703e30579"
    }

    STREAM_CHAT_WITH_DOC_REQUEST_BODY = {
        "thread_id": "67221190c04c60795742d473",
        "query": "Tell me about this doc",
        "llm_apikey": "66ff8e48882d3a6413037e52",
        "chat_session_id": "67221159c04c60795742d408",
        "file_id": "6722116bc04c60795742d46b",
        "tag": "67221169c04c60795742d45c.pdf",
        "embedding_api_key": "66ff8e48882d3a6413037e54",
        "brain_id": "671f780ec0a06e772eb1d1c3",
        "companypinecone": "companypinecone",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02
    }

    CUSTOM_GPT_WITH_DOC_REQUEST_BODY = {
        "thread_id": "672210edc04c60795742d3fc",
        "query": "tell me about this bot",
        "custom_gpt_id": "672210c5c04c60795742d37f",
        "llm_apikey": "66ff8e48882d3a6413037e52",
        "chat_session_id": "672210cec04c60795742d393",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02
    }

    TITLE_CHAT_GENERATE_REQUEST_BODY = {
        "title": "",
        "thread_id": "6721c3eac04c60795742ccee",
        "llm_apikey": "66ff8e48882d3a6413037e52",
        "chat_session_id": "6721c3c2c04c60795742cca1"
    }

    OPENAI_STORE_VECTOR_REQUEST_BODY = {
        "file_type": "pdf",
        "source": "s3_url",
        "file_url": "/documents/6721cfaec04c60795742ce70.pdf",
        "page_wise": "False",
        "vector_index": "66e1244ba6344e751faf730c",
        "dimensions": 1536,
        "id": "6721cfb3c04c60795742ce7f",
        "api_key_id": "66ff8e48882d3a6413037e54",
        "tag": "6721cfaec04c60795742ce70.pdf",
        "company_id": "66e1244ba6344e751faf730c",
        "brain_id": "671f780ec0a06e772eb1d1c3"
    }

    SCRAPE_URL_REQUEST_BODY = {
      "parent_prompt_ids": [ "671f77d120de5f44a6dc22c4" ],
      "company_id": "66e1244ba6344e751faf730c",
      "child_prompt_ids": []
    }

    TOOL_CHAT_WITH_OPENAI_REQUEST_BODY ={
      "thread_id": "6721c3eac04c60795742ccee",
      "query": "Hello",
      "llm_apikey": "66ff8e48882d3a6413037e52",
      "chat_session_id": "6721c3c2c04c60795742cca1",
      "company_id": "66e1244ba6344e751faf730c",
      "prompt_id":"66e26cde6532107128975d72", #Unknown Prompt ID
      "isregenerated": False,
      "image_url": '',
      "delay_chunk": 0.02
    }
    CANVAS_CHAT_WITH_OPENAI_REQUEST_BODY = {
        "old_thread_id": "6746f024b29446f0ce977c3b",
        "new_thread_id": "6746f053b29446f0ce977c8e",
        "query": "Add Keras Tool Link",
        "llm_apikey": "66ff8e48882d3a6413037e4f",
        "chat_session_id": "6745cb5a73414765941e7f9e",
        "company_id": "66e1244ba6344e751faf730c",
        "start_index": 620,
        "end_index": 760,
        "delay_chunk": 0.02,
        "code": "OPEN_AI"
    }
class DevTestPayload:
    SIMPLE_CHAT_WITH_OPENAI_REQUEST_BODY = {
    "thread_id": "66ab8b04161d8668d79a3b8f",
    "query": "give me a list of 10 basketball players of golden state",
    "llm_apikey": "66a0cf231bd0b30bb78e92be",
    "chat_session_id": "66ab8adc161d8668d79a3b79",
    "company_id": "666fd7cfb950158703e30579"
    }

    STREAM_CHAT_WITH_DOC_REQUEST_BODY = {
    "thread_id": "674fff8e9d72a82aea3ced66",
    "query": "Tell me about this doc",
    "llm_apikey": "66ff8e48882d3a6413037e4f",
    "chat_session_id": "674ffef39d72a82aea3ced14",
    "file_id": "674fff7f9d72a82aea3ced5c",
    "tag": "674fff7b9d72a82aea3ced4d.pdf",
    "embedding_api_key": "66ff8e48882d3a6413037e54",
    "brain_id": "67343cf3974f670346df5a30",
    "companypinecone": "companypinecone",
    "company_id": "66e1244ba6344e751faf730c",
    "delay_chunk": 0.02,
    "code": "OPEN_AI"
    }

    CUSTOM_GPT_WITH_DOC_REQUEST_BODY = {
        "thread_id": "6750014c9d72a82aea3cedf8",
        "query": "Framework for promoting Artificial Intelligence Research in India?",
        "custom_gpt_id": "675000dc9d72a82aea3cedb3",
        "llm_apikey": "66ff8e48882d3a6413037e4f",
        "chat_session_id": "675000e49d72a82aea3cedc2",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02,
        "code": "OPEN_AI"
    }

    TITLE_CHAT_GENERATE_REQUEST_BODY = {
        "title": "",
        "thread_id": "674ffeff9d72a82aea3ced32",
        "llm_apikey": "66ff8e48882d3a6413037e4f",
        "chat_session_id": "674ffef39d72a82aea3ced14",
        "code": "OPEN_AI"
    }

    OPENAI_STORE_VECTOR_REQUEST_BODY = {
        "file_type": "pdf",
        "source": "s3_url",
        "file_url": "/documents/674fff7b9d72a82aea3ced4d.pdf",
        "page_wise": "False",
        "vector_index": "66e1244ba6344e751faf730c",
        "dimensions": 1536,
        "id": "674fff7f9d72a82aea3ced5c",
        "api_key_id": "66ff8e48882d3a6413037e54",
        "tag": "674fff7b9d72a82aea3ced4d.pdf",
        "company_id": "66e1244ba6344e751faf730c",
        "brain_id": "67343cf3974f670346df5a30"
    }

    SCRAPE_URL_REQUEST_BODY = {
      "parent_prompt_ids": [ "675003159d72a82aea3cee5b" ],
      "company_id": "66e1244ba6344e751faf730c",
      "child_prompt_ids": []
    }

    TOOL_CHAT_WITH_OPENAI_REQUEST_BODY ={
        "thread_id": "674ffeff9d72a82aea3ced32",
        "query": "Hello",
        "llm_apikey": "66ff8e48882d3a6413037e4f",
        "chat_session_id": "674ffef39d72a82aea3ced14",
        "company_id": "66e1244ba6344e751faf730c",
        "delay_chunk": 0.02,
        "code": "OPEN_AI"
    }
    CANVAS_CHAT_WITH_OPENAI_REQUEST_BODY = {
        "old_thread_id": "6750003e9d72a82aea3ced92",
        "new_thread_id": "675000699d72a82aea3ced98",
        "query": "explain bit more ",
        "llm_apikey": "66ff8e48882d3a6413037e4f",
        "chat_session_id": "6750000c9d72a82aea3ced6e",
        "company_id": "66e1244ba6344e751faf730c",
        "start_index": 79,
        "end_index": 91,
        "delay_chunk": 0.02,
        "code": "OPEN_AI",
        "isregenerated": False   
    }

class QaTestPayload:
    SIMPLE_CHAT_WITH_OPENAI_REQUEST_BODY = {
    "thread_id": "66ab8b04161d8668d79a3b8f",
    "query": "give me a list of 10 basketball players of golden state",
    "llm_apikey": "66a0cf231bd0b30bb78e92be",
    "chat_session_id": "66ab8adc161d8668d79a3b79",
    "company_id": "666fd7cfb950158703e30579"
    }

    STREAM_CHAT_WITH_DOC_REQUEST_BODY = {
        "thread_id": "675007807b2f3da0f79d60fe",
        "query": "what is  in-swing?",
        "llm_apikey": "66fbac20866cbac15467df0e",
        "chat_session_id": "675007297b2f3da0f79d60af",
        "file_id": "675007417b2f3da0f79d60f3",
        "tag": "6750073d7b2f3da0f79d60e4.pdf",
        "embedding_api_key": "66fbac20866cbac15467df13",
        "brain_id": "671b8283c10e2353dd1f0e71",
        "companypinecone": "companypinecone",
        "company_id": "66e042e43dde18ff99b078e9",
        "delay_chunk": 0.02,
        "code": "OPEN_AI"
    }

    CUSTOM_GPT_WITH_DOC_REQUEST_BODY = {
        "thread_id": "6750082b7b2f3da0f79d61aa",
        "query": "list out Academic Institutes and centres",
        "custom_gpt_id": "675008037b2f3da0f79d615d",
        "llm_apikey": "66fbac20866cbac15467df0e",
        "chat_session_id": "675007c77b2f3da0f79d6114",
        "company_id": "66e042e43dde18ff99b078e9",
        "delay_chunk": 0.02,
        "code": "OPEN_AI"
    }

    TITLE_CHAT_GENERATE_REQUEST_BODY = {
        "title": "",
        "thread_id": "6750066f7b2f3da0f79d607b",
        "llm_apikey": "66fbac20866cbac15467df0e",
        "chat_session_id": "673d75b60f861861a563d383",
        "code": "OPEN_AI"
    }

    OPENAI_STORE_VECTOR_REQUEST_BODY = {
        "file_type": "pdf",
        "source": "s3_url",
        "file_url": "/documents/6750073d7b2f3da0f79d60e4.pdf",
        "page_wise": "False",
        "vector_index": "66e042e43dde18ff99b078e9",
        "dimensions": 1536,
        "id": "675007417b2f3da0f79d60f3",
        "api_key_id": "66fbac20866cbac15467df13",
        "tag": "6750073d7b2f3da0f79d60e4.pdf",
        "company_id": "66e042e43dde18ff99b078e9",
        "brain_id": "671b8283c10e2353dd1f0e71"
    }

    SCRAPE_URL_REQUEST_BODY = {
      "parent_prompt_ids": [ "675008737b2f3da0f79d61bd" ],
      "company_id": "66e042e43dde18ff99b078e9",
      "child_prompt_ids": []
    }

    TOOL_CHAT_WITH_OPENAI_REQUEST_BODY ={
        "thread_id": "6750066f7b2f3da0f79d607b",
        "query": "Hello",
        "llm_apikey": "66fbac20866cbac15467df0e",
        "chat_session_id": "673d75b60f861861a563d383",
        "company_id": "66e042e43dde18ff99b078e9",
        "delay_chunk": 0.02,
        "code": "OPEN_AI"
    }
    CANVAS_CHAT_WITH_OPENAI_REQUEST_BODY = {
        "old_thread_id": "675006d27b2f3da0f79d60a3",
        "new_thread_id": "675006f27b2f3da0f79d60a8",
        "query": "add imdb link",
        "llm_apikey": "66fbac20866cbac15467df0e",
        "chat_session_id": "675006b07b2f3da0f79d6082",
        "company_id": "66e042e43dde18ff99b078e9",
        "start_index": 1231,
        "end_index": 1243,
        "delay_chunk": 0.02,
        "code": "OPEN_AI",
        "isregenerated": False
    }
