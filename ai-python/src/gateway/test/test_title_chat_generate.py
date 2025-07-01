from dotenv import load_dotenv
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from src.gateway.api_router import api_router  # Adjust the import based on your file structure
from src.gateway.jwt_decode import get_user_data
from src.gateway.utils import run_test_and_log,get_environment_payloads
from src.gateway.config import TestCaseConfig

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
    return payloads.TITLE_CHAT_GENERATE_REQUEST_BODY 

api_url = TestCaseConfig.TITLE_CHAT_GENERATE_URL
invalid_type = TestCaseConfig.INVALID_TYPE
invalid_value = TestCaseConfig.INVALID_VALUE

# Positive Test Case
def test_title_chat_generate_valid_input(chat_input_data):
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_200_OK
    run_test_and_log("test_title_chat_generate_valid_input", status.HTTP_200_OK, response.status_code)

def test_title_chat_generate_additional_field(chat_input_data):
    chat_input_data["unexpected_field"] = "unexpected_value"
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_200_OK 
    run_test_and_log("test_title_chat_generate_additional_field", status.HTTP_200_OK, response.status_code)

# # Negative Test Cases
# # ===== Request body Missing value =====

def test_title_chat_generate_missing_thread_id(chat_input_data):
    chat_input_data.pop("thread_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    run_test_and_log("test_title_chat_generate_missing_thread_id", status.HTTP_400_BAD_REQUEST, response.status_code)

def test_title_chat_generate_missing_llm_apikey(chat_input_data):
    chat_input_data.pop("llm_apikey")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    run_test_and_log("test_title_chat_generate_missing_llm_apikey", status.HTTP_400_BAD_REQUEST, response.status_code)

def test_title_chat_generate_missing_chat_session_id(chat_input_data):
    chat_input_data.pop("chat_session_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    run_test_and_log("test_title_chat_generate_missing_chat_session_id", status.HTTP_400_BAD_REQUEST, response.status_code)

# ===== Request body Invalid value =====

def test_title_chat_generate_invalid_thread_id(chat_input_data):
    chat_input_data["thread_id"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_title_chat_generate_invalid_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_title_chat_generate_invalid_llm_apikey(chat_input_data):
    chat_input_data["llm_apikey"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_title_chat_generate_invalid_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_title_chat_generate_invalid_chat_session_id(chat_input_data):
    chat_input_data["chat_session_id"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_title_chat_generate_invalid_chat_session_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# ===== Request body Invalid value type =====

def test_title_chat_generate_invalid_thread_id_type(chat_input_data):
    chat_input_data["thread_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_title_chat_generate_invalid_thread_id_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_title_chat_generate_invalid_llm_apikey_type(chat_input_data):
    chat_input_data["llm_apikey"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_title_chat_generate_invalid_llm_apikey_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_title_chat_generate_invalid_chat_session_id_type(chat_input_data):
    chat_input_data["chat_session_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_title_chat_generate_invalid_chat_session_id_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)