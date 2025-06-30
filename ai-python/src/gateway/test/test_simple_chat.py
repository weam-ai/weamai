from dotenv import load_dotenv
import pytest
from fastapi import FastAPI, status, HTTPException
from fastapi.testclient import TestClient
from src.gateway.api_router import api_router  # Adjust the import based on your file structure
from src.gateway.jwt_decode import get_user_data
from src.gateway.utils import run_test_and_log,get_environment_payloads
from src.gateway.config import TestCaseConfig
from src.celery_worker_hub.extraction.utils import map_file_url,validate_file_url
import os

load_dotenv()

app = FastAPI()
app.include_router(api_router)

client = TestClient(app)

# Mock dependencies
def mock_get_user_data():
    return {"user_id": "test_user"}

app.dependency_overrides[get_user_data] = mock_get_user_data

api_url = TestCaseConfig.SIMPLE_CHAT_URL
invalid_type = TestCaseConfig.INVALID_TYPE
invalid_value = TestCaseConfig.INVALID_VALUE
img_url = TestCaseConfig.IMAGE_URL
invalid_img_url = TestCaseConfig.INVALID_IMAGE_URL
base_url_s3 = os.environ.get("AWS_S3_URL")
base_url_cdn = os.environ.get("AWS_CDN_URL")

payloads = get_environment_payloads()

@pytest.fixture
def chat_input_data():
    return payloads.SIMPLE_CHAT_WITH_OPENAI_REQUEST_BODY

# Positive Test Case
def ttest_stream_chat_with_openai_valid_input(chat_input_data):
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_200_OK
    run_test_and_log("test_stream_chat_with_openai", status.HTTP_200_OK, response.status_code)

def ttest_stream_chat_with_openai_additional_field(chat_input_data):
    chat_input_data["unexpected_field"] = "unexpected_value"
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_200_OK 
    run_test_and_log("test_stream_chat_with_openai_additional_field", status.HTTP_200_OK, response.status_code)

# Negative Test Cases
# ===== Request body Missing value =====

def test_stream_chat_with_openai_missing_thread_id(chat_input_data):
    chat_input_data.pop("thread_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_missing_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_openai_missing_query(chat_input_data):
    chat_input_data.pop("query")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_missing_query", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_openai_missing_llm_apikey(chat_input_data):
    chat_input_data.pop("llm_apikey")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_missing_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_openai_missing_chat_session_id(chat_input_data):
    chat_input_data.pop("chat_session_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_missing_chat_session_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_openai_missing_company_id(chat_input_data):
    chat_input_data.pop("company_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_missing_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# ===== Request body Invalid value =====

def test_stream_chat_with_openai_invalid_thread_id(chat_input_data):
    chat_input_data["thread_id"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_invalid_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_openai_invalid_llm_apikey(chat_input_data):
    chat_input_data["llm_apikey"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_invalid_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_openai_invalid_chat_session_id(chat_input_data):
    chat_input_data["chat_session_id"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_invalid_chat_session_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_openai_invalid_company_id(chat_input_data):
    chat_input_data["company_id"] =invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_invalid_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)


# ===== Request body Invalid value type =====

def test_stream_chat_with_openai_invalid_thread_id_type(chat_input_data):
    chat_input_data["thread_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_invalid_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_openai_invalid_llm_apikey_type(chat_input_data):
    chat_input_data["llm_apikey"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_invalid_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_openai_invalid_chat_session_id_type(chat_input_data):
    chat_input_data["chat_session_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_invalid_chat_session_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_stream_chat_with_openai_invalid_company_id_type(chat_input_data):
    chat_input_data["company_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_stream_chat_with_openai_invalid_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# Unit tests for URL mapping and validation
def test_map_img_url_s3():
    mapped_url = map_file_url(img_url, "s3_url")
    expected_url = base_url_cdn + img_url

    try:
        assert mapped_url == expected_url
        run_test_and_log("test_map_img_url_s3", status.HTTP_200_OK, status.HTTP_200_OK)
    except AssertionError as e:
        run_test_and_log("test_map_img_url_s3", status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)
        raise e

def test_map_img_url_public():
    mapped_url = map_file_url(img_url, "public_url")
    
    try:
        assert mapped_url == img_url
        run_test_and_log("test_map_img_url_public", status.HTTP_200_OK, status.HTTP_200_OK)
    except AssertionError as e:
        run_test_and_log("test_map_img_url_public", status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)
        raise e
    
def test_map_img_url_local():
    mapped_url = map_file_url(img_url, "public_url")
    
    try:
        assert mapped_url == img_url
        run_test_and_log("test_map_img_url_local", status.HTTP_200_OK, status.HTTP_200_OK)
    except AssertionError as e:
        run_test_and_log("test_map_img_url_local", status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)
        raise e
    
def test_validate_img_url_s3():
    url = base_url_cdn + img_url
    validated_url = validate_file_url(url, "s3_url")

    try:
        assert validated_url == url
        run_test_and_log("test_validate_img_url_s3", status.HTTP_200_OK, status.HTTP_200_OK)
    except AssertionError as e:
        run_test_and_log("test_validate_img_url_s3", status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)
        raise e

def test_invalid_img_url_s3():
    url = base_url_cdn + invalid_img_url

    with pytest.raises(HTTPException) as exc_info:
        validate_file_url(url, "s3_url")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    run_test_and_log("test_invalid_img_url_s3", status.HTTP_400_BAD_REQUEST, exc_info.value.status_code)

def test_invalid_img_url_public():
    url = base_url_cdn + invalid_img_url

    with pytest.raises(HTTPException) as exc_info:
        validate_file_url(url, "public_url")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    run_test_and_log("test_invalid_img_url_public", status.HTTP_400_BAD_REQUEST, exc_info.value.status_code)

def test_invalid_img_url_local():
    url = base_url_cdn + invalid_img_url

    with pytest.raises(HTTPException) as exc_info:
        validate_file_url(url, "local_file")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    run_test_and_log("test_invalid_img_url_local", status.HTTP_400_BAD_REQUEST, exc_info.value.status_code)