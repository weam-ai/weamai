from dotenv import load_dotenv
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from src.gateway.api_router import api_router
from src.gateway.jwt_decode import get_user_data
from src.gateway.utils import run_test_and_log,get_environment_payloads
from src.gateway.config import TestCaseConfig
from src.chatflow_langchain.repositories.additional_prompts import PromptRepository

load_dotenv()

prompt_repo = PromptRepository()

app = FastAPI()
app.include_router(api_router)

client = TestClient(app)

def mock_get_user_data():
    return {
        "_id": "user_id_example",
        "email": "test_user@example.com",
        "fname": "John",
        "lname": "Doe",
        "profile": {
            "name": "John Doe",
            "uri": "http://example.com/profile/johndoe",
            "mime_type": "image/png",
            "id": "profile_id_example"
        }
    }

app.dependency_overrides[get_user_data] = mock_get_user_data


api_url = TestCaseConfig.SCRAPE_URL
invalid_type = TestCaseConfig.INVALID_TYPE
invalid_value = TestCaseConfig.INVALID_VALUE

payloads = get_environment_payloads()

@pytest.fixture
def scrape_url_data():
    return payloads.SCRAPE_URL_REQUEST_BODY

# Positive Test Case
def test_scrape_url_valid_input(scrape_url_data):
    prompt_repo.initialization(scrape_url_data['parent_prompt_ids'][0],"prompts")
    response = client.post(api_url, json=scrape_url_data)
    assert response.status_code == status.HTTP_200_OK
    run_test_and_log("test_scrape_url_valid_input", status.HTTP_200_OK, response.status_code)

def test_scrape_url_additional_field(scrape_url_data):
    scrape_url_data["unexpected_field"] = "unexpected_value"
    response = client.post(api_url, json=scrape_url_data)
    assert response.status_code == status.HTTP_200_OK 
    run_test_and_log("test_scrape_url_additional_field", status.HTTP_200_OK, response.status_code)


# # Negative Test Cases
# # ===== Request body Missing value =====

def test_scrape_url_missing_prompt_ids(scrape_url_data):
    scrape_url_data.pop("parent_prompt_ids")
    response = client.post(api_url, json=scrape_url_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_scrape_url_missing_parent_prompt_ids", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_scrape_url_missing_company_id(scrape_url_data):
    scrape_url_data.pop("company_id")
    response = client.post(api_url, json=scrape_url_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_scrape_url_missing_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_scrape_url_missing_parent_brain_id(scrape_url_data):
#     scrape_url_data.pop("parent_brain_id")
#     response = client.post(api_url, json=scrape_url_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_scrape_url_missing_parent_brain_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_scrape_url_missing_child_brain_ids(scrape_url_data):
#     scrape_url_data.pop("child_brain_ids")
#     response = client.post(api_url, json=scrape_url_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_scrape_url_missing_child_brain_ids", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_scrape_url_missing_llm_apikey(scrape_url_data):
#     scrape_url_data.pop("llm_apikey")
#     response = client.post(api_url, json=scrape_url_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_scrape_url_missing_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# # ===== Request body Invalid value =====

def test_scrape_url_invalid_parent_prompt_ids(scrape_url_data):
    scrape_url_data["parent_prompt_ids"]=invalid_value
    response = client.post(api_url, json=scrape_url_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_scrape_url_invalid_parent_prompt_ids", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_scrape_url_invalid_company_id(scrape_url_data):
    scrape_url_data["company_id"]=invalid_value
    response = client.post(api_url, json=scrape_url_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_scrape_url_invalid_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_scrape_url_invalid_parent_brain_id(scrape_url_data):
#     scrape_url_data["parent_brain_id"]=invalid_value
#     response = client.post(api_url, json=scrape_url_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_scrape_url_invalid_parent_brain_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_scrape_url_invalid_child_brain_ids(scrape_url_data):
#     scrape_url_data["child_brain_ids"]=invalid_value
#     response = client.post(api_url, json=scrape_url_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_scrape_url_invalid_child_brain_ids", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_scrape_url_invalid_llm_apikey(scrape_url_data):
#     scrape_url_data["llm_apikey"]=invalid_value
#     response = client.post(api_url, json=scrape_url_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_scrape_url_invalid_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)



