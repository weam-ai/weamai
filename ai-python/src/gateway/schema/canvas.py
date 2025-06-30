from typing import Optional
from pydantic import BaseModel, Field, field_validator
from src.gateway.schema.utils import validate_id_field

class CanvasBase(BaseModel):
      old_thread_id: str = Field(..., description="A unique row identifier for the thread collection, which is defined in MongoDB.")
      new_thread_id: str = Field(..., description="A unique row identifier for the thread collection, which is defined in MongoDB.")
      llm_apikey: str = Field(..., description="A unique row identifier for the  large language models (LLMs) collection.")
      chat_session_id: str = Field(..., description="A field in the thread collection indicating the session ID for the chat; it remains the same for the same chat session and changes for new sessions.")
      query: str = Field(..., description="The message input by the user to the model.")
      start_index:int=Field(..., description="The message selected start index of  text by the user.")
      end_index:int=Field(..., description="The message selected start end of  text by the user.")
      company_id: str = Field(...,description="company id required")
      companymodel: str = Field("companymodel", description="The name of the collection.")
      threadmodel: str = Field("messages", description="The name of the collection.")
      companypinecone: str = Field(default="companypinecone",description="Pinecone index used by the company for vector operations.")
      custom_gpt_collection: str = Field(default="customgpt",description="Pinecone index used by the company for vector operations.")
      delay_chunk:float=Field(0.05,description="chunk delay response flag")
      code:str=Field("OPEN_AI",description="Code to decide which llm to use for response")
      model_name:Optional[str] = Field(None,description="Name of the Model selected")
      chat_docs_collection:str=Field("chatdocs",description="chat docs collection")
      provider:str=Field(None,description="Provider to decide which llm to use for response")
      isregenerated:bool = Field(False,description='Flag for regeneration')
      msgCredit:Optional[float]=Field(0,description="Message Credit")
      is_paid_user:bool=Field(True,description='Plan Type Flag')

      @field_validator('new_thread_id', 'old_thread_id','llm_apikey', 'chat_session_id', mode='before')
      def validate_id_fields(cls, value, field_info):
            return validate_id_field(value, field_info.field_name)