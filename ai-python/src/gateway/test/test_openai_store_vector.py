# from dotenv import load_dotenv
# import pytest
# from fastapi import FastAPI, status
# from fastapi.testclient import TestClient
# from src.gateway.api_router import api_router  # Adjust the import based on your file structure
# from src.gateway.jwt_decode import get_user_data
# from src.gateway.config import TestCaseConfig
# from src.gateway.utils import run_test_and_log

# load_dotenv()

# app = FastAPI()
# app.include_router(api_router)

# client = TestClient(app)

# # Mock dependencies
# def mock_get_user_data():
#     return {"user_id": "test_user"}

# app.dependency_overrides[get_user_data] = mock_get_user_data

# @pytest.fixture
# def file_input_data():
#     return TestCaseConfig.OPENAI_STORE_VECTOR_REQUEST_BODY

# api_url = TestCaseConfig.OPENAI_STORE_VECTOR_URL  # Make sure this matches your config
# invalid_type = TestCaseConfig.INVALID_TYPE
# invalid_value = TestCaseConfig.INVALID_VALUE

# # Positive Test Case
# def test_openai_store_vector_valid_input(file_input_data):
#     response = client.post(api_url, json=file_input_data)
    
#     assert response.status_code == status.HTTP_200_OK
#     run_test_and_log("test_openai_store_vector_valid_input", status.HTTP_200_OK, response.status_code)


# def test_openai_store_vector_additional_field(file_input_data):
#     file_input_data["unexpected_field"] = "unexpected_value"
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_200_OK 
#     run_test_and_log("test_openai_store_vector_additional_field", status.HTTP_200_OK, response.status_code)

# # Negative Test Cases
# # ===== Request body Missing value =====

# def test_openai_store_vector_missing_file_type(file_input_data):
#     file_input_data.pop("file_type")
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_missing_file_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_missing_source(file_input_data):
#     file_input_data.pop("source")
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_missing_source", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_missing_file_url(file_input_data):
#     file_input_data.pop("file_url")
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_missing_file_url", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_missing_vector_index(file_input_data):
#     file_input_data.pop("vector_index")
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_missing_vector_index", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_missing_id(file_input_data):
#     file_input_data.pop("id")
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_missing_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_missing_api_key_id(file_input_data):
#     file_input_data.pop("api_key_id")
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_missing_api_key_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_missing_tag(file_input_data):
#     file_input_data.pop("tag")
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_missing_tag", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_missing_company_id(file_input_data):
#     file_input_data.pop("company_id")
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_missing_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# # ===== Request body Invalid value =====

# def test_openai_store_vector_invalid_file_type(file_input_data):
#     file_input_data["file_type"] = invalid_value
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_invalid_file_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_source(file_input_data):
#     file_input_data["source"] = invalid_value
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_invalid_source", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_file_url(file_input_data):
#     file_input_data["file_url"] = invalid_value
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_invalid_file_url", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_page_wise(file_input_data):
#     file_input_data["page_wise"] = invalid_value
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_invalid_page_wise", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_vector_index(file_input_data):
#     file_input_data["vector_index"] = invalid_value
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_invalid_vector_index", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_id(file_input_data):
#     file_input_data["id"] = invalid_value
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_invalid_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_api_key_id(file_input_data):
#     file_input_data["api_key_id"] = invalid_value
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_invalid_api_key_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_tag(file_input_data):
#     file_input_data["tag"] = invalid_value
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_invalid_tag", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_company_id(file_input_data):
#     file_input_data["company_id"] = invalid_value
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_openai_store_vector_invalid_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# # ===== Request body Invalid value type =====

# def test_openai_store_vector_invalid_file_type_type(file_input_data):
#     file_input_data["file_type"] = invalid_type
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_file_upload_invalid_file_type_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_source_type(file_input_data):
#     file_input_data["source"] = invalid_type
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_file_upload_invalid_source_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_file_url_type(file_input_data):
#     file_input_data["file_url"] = invalid_type
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_file_upload_invalid_file_url_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_vector_index_type(file_input_data):
#     file_input_data["vector_index"] = invalid_type
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_file_upload_invalid_vector_index_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_id_type(file_input_data):
#     file_input_data["id"] = invalid_type
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_file_upload_invalid_id_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_api_key_id_type(file_input_data):
#     file_input_data["api_key_id"] = invalid_type
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_file_upload_invalid_api_key_id_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_tag_type(file_input_data):
#     file_input_data["tag"] = invalid_type
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_file_upload_invalid_tag_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

# def test_openai_store_vector_invalid_company_id_type(file_input_data):
#     file_input_data["company_id"] = invalid_type
#     response = client.post(api_url, json=file_input_data)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     run_test_and_log("test_file_upload_invalid_company_id_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)
