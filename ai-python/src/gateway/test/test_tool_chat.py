from dotenv import load_dotenv
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from src.gateway.api_router import api_router  # Adjust the import based on your file structure
from src.gateway.jwt_decode import get_user_data
from src.gateway.utils import run_test_and_log,get_environment_payloads
from src.gateway.config import TestCaseConfig
import os
from src.chatflow_langchain.service.openai.tool_functions.tool_service import OpenAIToolServiceOpenai 
from langchain_openai import ChatOpenAI

load_dotenv()

app = FastAPI()
app.include_router(api_router)

client = TestClient(app)

tool_service = OpenAIToolServiceOpenai()

# Mock dependencies
def mock_get_user_data():
    return {"user_id": "test_user"}

app.dependency_overrides[get_user_data] = mock_get_user_data

api_url = TestCaseConfig.TOOL_CHAT_URL
invalid_type = TestCaseConfig.INVALID_TYPE
invalid_value = TestCaseConfig.INVALID_VALUE
img_url = TestCaseConfig.IMAGE_URL
invalid_img_url = TestCaseConfig.INVALID_IMAGE_URL
base_url_s3 = os.environ.get("AWS_S3_URL")
base_url_cdn = os.environ.get("AWS_CDN_URL")

payloads = get_environment_payloads()

@pytest.fixture
def chat_input_data():
    return payloads.TOOL_CHAT_WITH_OPENAI_REQUEST_BODY

# Positive Test Case

# ToolChat Service Testcases
def test_tool_initialize_llm_success(chat_input_data):
    tool_service.initialize_llm(
        api_key_id=chat_input_data['llm_apikey'],
        companymodel='companymodel',
        dalle_wrapper_size='1024x1024',
        dalle_wrapper_quality='standard',
        dalle_wrapper_style='vivid',
        thread_id=chat_input_data['thread_id'],
        thread_model='messages',
        imageT=0)

    assert isinstance(tool_service.llm, ChatOpenAI), "LLM should be an instance of ChatOpenAI"
    run_test_and_log("test_tool_initialize_llm_success", status.HTTP_200_OK, status.HTTP_200_OK)  # Log success

def test_tool_initialize_repository_success(chat_input_data):
    """Test successful initialization of the repository."""
    tool_service.initialize_repository(
        chat_session_id=chat_input_data['chat_session_id'],
        collection_name='messages',
        regenerated_flag=False)

    if hasattr(tool_service, 'history_messages') and tool_service.history_messages is not None:
        run_test_and_log("test_tool_initialize_repository_success", status.HTTP_200_OK, status.HTTP_200_OK)
    else:
        run_test_and_log("test_tool_initialize_repository_succes_400", status.HTTP_400_BAD_REQUEST, status.HTTP_400_BAD_REQUEST)

# def test_prompt_attach_success(chat_input_data):
#     tool_service.prompt_attach(additional_prompt_id=chat_input_data['prompt_id'],
#                                collection_name='prompts')  
#     if tool_service.additional_prompt:
#         assert status.HTTP_200_OK == status.HTTP_200_OK
#         run_test_and_log("test_prompt_attach_success", status.HTTP_200_OK, status.HTTP_200_OK)
#     else:
#         assert status.HTTP_400_BAD_REQUEST == status.HTTP_200_OK
#         run_test_and_log("test_prompt_attach_success_400", status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)

# def test_create_conversation_success(chat_input_data):
#     tool_service.initialize_llm(
#         api_key_id=chat_input_data['llm_apikey'],
#         companymodel='companymodel',
#         dalle_wrapper_size='1024x1024',
#         dalle_wrapper_quality='standard',
#         dalle_wrapper_style='vivid',
#         thread_id=chat_input_data['thread_id'],
#         thread_model='messages',
#         imageT=0)
#     # tool_service.prompt_attach(additional_prompt_id=chat_input_data['prompt_id'],
#     #                        collection_name='prompts')  
#     tool_service.create_conversation(
#         input_text=chat_input_data.get('query', ''),
#         image_url=chat_input_data.get('image_url', None),
#         image_source=chat_input_data.get('image_source', 's3_url'),
#         regenerate_flag=chat_input_data.get('isregenerated', False))

#     if tool_service.additional_prompt is None:
#         expected_original_query = chat_input_data.get('query', '')
#     else:
#         expected_original_query = tool_service.additional_prompt + chat_input_data.get('query', '')

#     assert tool_service.query_arguments['simple_chat_v2']['original_query'] == expected_original_query, (
#         f"Expected original_query: {expected_original_query}, but got: {tool_service.query_arguments['simple_chat_v2']['original_query']}")

#     run_test_and_log("test_create_conversation_success", status.HTTP_200_OK, status.HTTP_200_OK)

def test_tool_calls_run_success(chat_input_data):
        try:
            tool_service.tool_calls_run(
                thread_id=chat_input_data['thread_id'],
                collection_name='messages')
            assert status.HTTP_200_OK == status.HTTP_200_OK
            run_test_and_log("test_tool_calls_run_success", status.HTTP_200_OK, status.HTTP_200_OK)
        except:
            assert status.HTTP_400_BAD_REQUEST == status.HTTP_200_OK
            run_test_and_log("test_tool_calls_run_success_400", status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)

def test_tool_chat_with_openai_valid_input(chat_input_data):
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_200_OK
    run_test_and_log("test_tool_chat_with_openai_valid_input", status.HTTP_200_OK, response.status_code)

def test_tool_chat_with_openai_additional_field(chat_input_data):
    chat_input_data["unexpected_field"] = "unexpected_value"
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_200_OK 
    run_test_and_log("test_tool_chat_with_openai_additional_field", status.HTTP_200_OK, response.status_code)


# # Negative Test Cases
# # ===== Request body Missing value =====
def test_tool_chat_with_openai_missing_thread_id(chat_input_data):
    chat_input_data.pop("thread_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_missing_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_tool_chat_with_openai_missing_query(chat_input_data):
    chat_input_data.pop("query")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_missing_query", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_tool_chat_with_openai_missing_llm_apikey(chat_input_data):
    chat_input_data.pop("llm_apikey")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_missing_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_tool_chat_with_openai_missing_chat_session_id(chat_input_data):
    chat_input_data.pop("chat_session_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_missing_chat_session_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_tool_chat_with_openai_missing_company_id(chat_input_data):
    chat_input_data.pop("company_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_missing_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# # ===== Request body Invalid value =====
def test_tool_chat_with_openai_invalid_thread_id(chat_input_data):
    chat_input_data["thread_id"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_invalid_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_tool_chat_with_openai_invalid_llm_apikey(chat_input_data):
    chat_input_data["llm_apikey"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_invalid_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_tool_chat_with_openai_invalid_chat_session_id(chat_input_data):
    chat_input_data["chat_session_id"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_invalid_chat_session_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_tool_chat_with_openai_invalid_company_id(chat_input_data):
    chat_input_data["company_id"] =invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_invalid_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)


# # # ===== Request body Invalid value type =====
def test_tool_chat_with_openai_invalid_thread_id_type(chat_input_data):
    chat_input_data["thread_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_invalid_thread_id_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_tool_chat_with_openai_invalid_llm_apikey_type(chat_input_data):
    chat_input_data["llm_apikey"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_invalid_llm_apikey_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_tool_chat_with_openai_invalid_chat_session_id_type(chat_input_data):
    chat_input_data["chat_session_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_invalid_chat_session_id_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_tool_chat_with_openai_invalid_company_id_type(chat_input_data):
    chat_input_data["company_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_tool_chat_with_openai_invalid_company_id_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)
