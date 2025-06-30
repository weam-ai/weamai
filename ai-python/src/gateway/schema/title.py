from pydantic import BaseModel, Field, field_validator
from src.gateway.schema.utils import validate_id_field

class TitleBase(BaseModel):
      thread_id: str = Field("1", description="A unique row identifier for the thread collection, which is defined in MongoDB.")
      llm_apikey: str = Field("1", description="A unique row identifier for the model collection, specifically referencing gpt-3.5-turbo and other large language models (LLMs).")
      companymodel: str = Field("companymodel", description="The name of the collection.")
      threadmodel: str = Field("messages", description="The name of the collection.")
      chat_session_id: str = Field("1", description="A field in the thread collection indicating the session ID for the chat; it remains the same for the same chat session and changes for new sessions.")
      chatmodel:str=Field("chat",description="the name of the collection for acessing the chat session id")
      chatmembermodel:str=Field("chatmember",description="the name of the collection for acessing the chat member id")
      code:str=Field("OPEN_AI",description="Code to decide which llm to use for response")
      provider:str=Field("DEEPSEEK",description="Provider to decide which llm to use for response")
      company_id:str=Field(None,description="registerd company id")
      model_name:str=Field(None,description="model name")

      @field_validator('thread_id', 'llm_apikey', 'chat_session_id', mode='before')
      def validate_id_fields(cls, value, field_info):
            return validate_id_field(value, field_info.field_name)