from dotenv import load_dotenv
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from src.gateway.api_router import api_router  # Adjust the import based on your file structure
from src.gateway.jwt_decode import get_user_data
from src.gateway.utils import run_test_and_log,get_environment_payloads
from src.gateway.config import TestCaseConfig
from src.chatflow_langchain.service.openai.canvas.canvas_manager import OpenAICanvasService 
from langchain_openai import ChatOpenAI
from src.chatflow_langchain.controller.canvas import CanvasController

load_dotenv()

app = FastAPI()
app.include_router(api_router)

client = TestClient(app)

canvas_service = OpenAICanvasService()
canvas_controller = CanvasController()

# Mock dependencies
def mock_get_user_data():
    return {"user_id": "test_user"}

app.dependency_overrides[get_user_data] = mock_get_user_data

api_url = TestCaseConfig.CANVAS_CHAT_URL
invalid_type = TestCaseConfig.INVALID_TYPE
invalid_value = TestCaseConfig.INVALID_VALUE

payloads = get_environment_payloads()

@pytest.fixture
def chat_input_data():
    return payloads.CANVAS_CHAT_WITH_OPENAI_REQUEST_BODY

def test_canvas_initialize_llm_success(chat_input_data):
    canvas_service.initialize_llm(
        api_key_id=chat_input_data['llm_apikey'],
        companymodel='companymodel')

    assert isinstance(canvas_service.llm, ChatOpenAI), "LLM should be an instance of ChatOpenAI"
    run_test_and_log("test_canvas_initialize_llm_success", status.HTTP_200_OK, status.HTTP_200_OK)  # Log success

def test_canvas_initialize_repository_success(chat_input_data): 
    """Test successful initialization of the repository."""
    canvas_service.initialize_thread_data(
        thread_id=chat_input_data['old_thread_id'], 
        collection_name="messages",
        regenerated_flag=chat_input_data['isregenerated']
    )
    canvas_service.initialize_repository(
        chat_session_id=chat_input_data['chat_session_id'],
        chat_collection_name='messages')

    if hasattr(canvas_service, 'history_messages') and canvas_service.history_messages is not None:
        run_test_and_log("test_canvas_initialize_repository_success", status.HTTP_200_OK, status.HTTP_200_OK)
    else:
        run_test_and_log("test_canvas_initialize_repository_succes_400", status.HTTP_400_BAD_REQUEST, status.HTTP_400_BAD_REQUEST)

def test_canvas_initialize_thread_data_success(chat_input_data):
    canvas_service.initialize_thread_data(thread_id=chat_input_data['old_thread_id'],regenerated_flag=chat_input_data['isregenerated'],
            collection_name="messages")  
    if canvas_service.api_type:
        assert status.HTTP_200_OK == status.HTTP_200_OK
        run_test_and_log("test_canvas_initialize_thread_data_success", status.HTTP_200_OK, status.HTTP_200_OK)
    else:
        assert status.HTTP_400_BAD_REQUEST == status.HTTP_200_OK
        run_test_and_log("test_canvas_initialize_thread_data_success_400", status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)

def test_canvas_initialization_service_code_success(chat_input_data):
    canvas_controller.initialization_service_code(code=chat_input_data['code'])  
    if canvas_controller.code:
        assert status.HTTP_200_OK == status.HTTP_200_OK
        run_test_and_log("test_canvas_initialization_service_code_success", status.HTTP_200_OK, status.HTTP_200_OK)
    else:
        assert status.HTTP_400_BAD_REQUEST == status.HTTP_200_OK
        run_test_and_log("test_canvas_initialization_service_code_success_400", status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)

def test_canvas_service_hub_handler_success(chat_input_data):
    response = canvas_controller.service_hub_handler(chat_input_data) 
    if response:
        assert status.HTTP_200_OK == status.HTTP_200_OK
        run_test_and_log("test_canvas_service_hub_handler_success", status.HTTP_200_OK, status.HTTP_200_OK)
    else:
        assert status.HTTP_400_BAD_REQUEST == status.HTTP_200_OK
        run_test_and_log("test_canvas_service_hub_handler_success_400", status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)

def test_canvas_chat_with_openai_valid_input(chat_input_data):
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_200_OK
    run_test_and_log("test_canvas_chat_with_openai_valid_input", status.HTTP_200_OK, response.status_code)

def test_canvas_chat_with_openai_additional_field(chat_input_data):
    chat_input_data["unexpected_field"] = "unexpected_value"
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_200_OK 
    run_test_and_log("test_canvas_chat_with_openai_additional_field", status.HTTP_200_OK, response.status_code)


# # Negative Test Cases
# # ===== Request body Missing value =====
def test_canvas_chat_with_openai_missing_old_thread_id(chat_input_data):
    chat_input_data.pop("old_thread_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_missing_old_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_missing_new_thread_id(chat_input_data):
    chat_input_data.pop("new_thread_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_missing_new_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_missing_query(chat_input_data):
    chat_input_data.pop("query")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_missing_query", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_missing_llm_apikey(chat_input_data):
    chat_input_data.pop("llm_apikey")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_missing_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_missing_chat_session_id(chat_input_data):
    chat_input_data.pop("chat_session_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_missing_chat_session_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_missing_company_id(chat_input_data):
    chat_input_data.pop("company_id")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_missing_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_missing_start_index(chat_input_data):
    chat_input_data.pop("start_index")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_missing_start_index", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_missing_end_index(chat_input_data):
    chat_input_data.pop("end_index")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_missing_end_index", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_missing_end_index(chat_input_data):
    chat_input_data.pop("end_index")
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_missing_end_index", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)
    

# # ===== Request body Invalid value =====
def test_canvas_chat_with_openai_invalid_old_thread_id(chat_input_data):
    chat_input_data["old_thread_id"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_invalid_old_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_invalid_new_thread_id(chat_input_data):
    chat_input_data["new_thread_id"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_invalid_new_thread_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_invalid_llm_apikey(chat_input_data):
    chat_input_data["llm_apikey"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_invalid_llm_apikey", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_invalid_chat_session_id(chat_input_data):
    chat_input_data["chat_session_id"] = invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_invalid_chat_session_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_invalid_company_id(chat_input_data):
    chat_input_data["company_id"] =invalid_value
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_invalid_company_id", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)


# # # ===== Request body Invalid value type =====
def test_canvas_chat_with_openai_invalid_old_thread_id_type(chat_input_data):
    chat_input_data["old_thread_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_invalid_old_thread_id_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_invalid_new_thread_id_type(chat_input_data):
    chat_input_data["new_thread_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_invalid_new_thread_id_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_invalid_llm_apikey_type(chat_input_data):
    chat_input_data["llm_apikey"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_invalid_llm_apikey_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_invalid_chat_session_id_type(chat_input_data):
    chat_input_data["chat_session_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_invalid_chat_session_id_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)

def test_canvas_chat_with_openai_invalid_company_id_type(chat_input_data):
    chat_input_data["company_id"] = invalid_type
    response = client.post(api_url, json=chat_input_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    run_test_and_log("test_canvas_chat_with_openai_invalid_company_id_type", status.HTTP_422_UNPROCESSABLE_ENTITY, response.status_code)
