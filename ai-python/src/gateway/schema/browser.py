from typing import Optional
from pydantic import BaseModel, Field, field_validator
from src.gateway.schema.utils import validate_id_field

class BrowserChatBase(BaseModel):
    thread_id: str = Field(..., description="A unique row identifier for the thread collection, which is defined in MongoDB.")
    company_id: str = Field(..., description="Company ID required.")
    prompt_id: Optional[str] = Field(default=None, description="The identifier for the additional prompt provided by the user, if any.")
    query: str = Field(..., description="The message input by the user to the model.")
    llm_apikey: str = Field(..., description="A unique row identifier for the model collection, specifically referencing GPT-3.5-turbo and other large language models (LLMs).")
    chat_session_id: str = Field(..., description="A field in the thread collection indicating the session ID for the chat; it remains the same for the same chat session and changes for new sessions.")
    companymodel: str = Field("companymodel", description="The name of the company collection.")
    threadmodel: str = Field("messages", description="The name of the thread collection.")
    promptmodel: str = Field("prompts", description="The name of the additional prompt collection.")
    isregenerated:bool = Field(False,description='Flag for regeneration')
    code:str=Field("OPEN_AI",description="Code to decide which llm to use for response")
    model_name:Optional[str] = Field(None,description="Name of the Model selected")
    delay_chunk:float=Field(0.3,description="chunk delay response flag")
    provider:str=Field(None,description="Provider to decide which llm to use for response")
    msgCredit:Optional[float]=Field(0,description="Message Credit")
    is_paid_user:bool=Field(True,description='Plan Type Flag')
    @field_validator('company_id', 'thread_id', 'llm_apikey', 'chat_session_id', mode='before')
    def validate_id_fields(cls, value, field_info):
        return validate_id_field(value, field_info.field_name)