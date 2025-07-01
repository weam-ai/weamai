from dotenv import load_dotenv
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from src.gateway.api_router import api_router  # Adjust the import based on your file structure
from src.gateway.jwt_decode import get_user_data
from src.gateway.config import TestCaseConfig
from src.gateway.utils import run_test_and_log,get_environment_payloads

load_dotenv()

app = FastAPI()
app.include_router(api_router)

client = TestClient(app)

# Mock dependencies
def mock_get_user_data():
    return {"user_id": "test_user"}

app.dependency_overrides[get_user_data] = mock_get_user_data

payloads = get_environment_payloads()

@pytest.fixture
def chat_input_data():
    return payloads.STREAM_CHAT_WITH_DOC_REQUEST_BODY

api_url = TestCaseConfig.STREAM_CHAT_DOC_URL
invalid_type = TestCaseConfig.INVALID_TYPE
invalid_value = TestCaseConfig.INVALID_VALUE

# Positive Test Case
def test_stream_chat_with_doc_valid_input(chat_input_data):
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_200_OK
    run_test_and_log("test_stream_chat_with_doc_valid_input", status.HTTP_200_OK, response.status_code)

# Negative Test Cases
# ===== Request body Missing value =====

def test_stream_chat_with_doc_missing_thread_id(chat_input_data):
    chat_input_data.pop("thread_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_missing_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_missing_query(chat_input_data):
    chat_input_data.pop("query")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_missing_query", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_missing_llm_apikey(chat_input_data):
    chat_input_data.pop("llm_apikey")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_missing_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_missing_chat_session_id(chat_input_data):
    chat_input_data.pop("chat_session_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_missing_chat_session_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_missing_file_id(chat_input_data):
    chat_input_data.pop("file_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_missing_file_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_missing_tag(chat_input_data):
    chat_input_data.pop("tag")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_missing_tag", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_missing_embedding_api_key(chat_input_data):
    chat_input_data.pop("embedding_api_key")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_missing_embedding_api_key", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_missing_company_id(chat_input_data):
    chat_input_data.pop("company_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_missing_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# ===== Request body Invalid value =====

def test_stream_chat_with_doc_invalid_thread_id(chat_input_data):
    chat_input_data["thread_id"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_invalid_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_invalid_llm_apikey(chat_input_data):
    chat_input_data["llm_apikey"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_invalid_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_invalid_chat_session_id(chat_input_data):
    chat_input_data["chat_session_id"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_invalid_chat_session_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_invalid_embedding_api_key(chat_input_data):
    chat_input_data["embedding_api_key"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_invalid_embedding_api_key", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_invalid_company_id(chat_input_data):
    chat_input_data["company_id"] =invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_invalid_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)


# ===== Request body Invalid value type =====

def test_stream_chat_with_doc_invalid_thread_id_type(chat_input_data):
    chat_input_data["thread_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_invalid_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_invalid_llm_apikey_type(chat_input_data):
    chat_input_data["llm_apikey"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_invalid_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_invalid_chat_session_id_type(chat_input_data):
    chat_input_data["chat_session_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_invalid_chat_session_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_invalid_embedding_api_key_type(chat_input_data):
    chat_input_data["embedding_api_key"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_invalid_embedding_api_key", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_doc_invalid_company_id_type(chat_input_data):
    chat_input_data["company_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_doc_invalid_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)