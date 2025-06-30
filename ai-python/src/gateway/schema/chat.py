from typing import Optional,Union
from pydantic import BaseModel, Field,field_validator
from src.gateway.schema.utils import validate_id_field, IMAGE_SOURCE_BUCKET

class ChatBase(BaseModel):
      thread_id: str = Field(..., description="A unique row identifier for the thread collection, which is defined in MongoDB.")
      company_id: str = Field(...,description="company id required")
      prompt_id: Optional[str] = Field(default=None,description="The identifier for the additional prompt associated with provided by user if any.")
      query: str = Field(..., description="The message input by the user to the model.")
      llm_apikey: str = Field(..., description="A unique row identifier for the model collection, specifically referencing gpt-3.5-turbo and other large language models (LLMs).")
      chat_session_id: str = Field(..., description="A field in the thread collection indicating the session ID for the chat; it remains the same for the same chat session and changes for new sessions.")
      companymodel: str = Field("companymodel", description="The name of the collection.")
      threadmodel: str = Field("messages", description="The name of the collection.")
      promptmodel:str=Field("prompts",description="the name of additional prompt collection")
      image_url:Optional[Union[str, list[str]]]=Field(None,description="image_url pass for analysis")
      delay_chunk:float=Field(0.3,description="chunk delay response flag")
      image_source: str = Field(default=IMAGE_SOURCE_BUCKET, description="Image source of the file (e.g., S3 bucket URL).")
      model_name:Optional[str] = Field(None,description="Name of the Model selected")
      provider:str=Field(None,description="Provider to decide which llm to use for response")
      msgCredit:Optional[float]=Field(0,description="Message Credit")
      is_paid_user:bool=Field(True,description='Plan Type Flag')
      @field_validator('company_id', 'thread_id', 'llm_apikey', 'chat_session_id', mode='before')
      def validate_id_fields(cls, value, field_info):
            return validate_id_field(value, field_info.field_name)

class DocChatBase(ChatBase):
      file_id:Optional[Union[str, list[str]]] = Field(..., description="A unique row identifier for a file collection, which is defined in MongoDB.")
      tag: Optional[Union[str, list[str]]] = Field(..., description="The name of the file, which is stored in the file collection as name.")
      brain_id: str = Field("uwp", description="Currently represents a brain name, with plans for it to be represented by a brain ID in the future.")
      pinecone_apikey_id: str = Field(None, description="A unique row identifier for the companypinecone collection, which is defined in MongoDB.")
      embedding_api_key: str = Field(None, description="A unique row identifier for the model collection, specifically referencing the text-embedding-3-small and other embedding models.")
      companypinecone: str = Field("companypinecone", description="The name of the companypinecone collection, which is defined in MongoDB.")
      isMedia:bool=Field(True,description="flag of media using")
      file_collection:str=Field("file",description="file collection name")
      isregenerated:bool=Field(False,description="Flag for regeneration")
      code:str=Field("OPEN_AI",description="Code to decide which llm to use for response")
      chat_docs_collection:str=Field("chatdocs",description="chat docs collection")
      msgCredit:Optional[float]=Field(0,description="Message Credit")
      is_paid_user:bool=Field(True,description='Plan Type Flag')
      @field_validator('embedding_api_key','thread_id','llm_apikey','chat_session_id','company_id', mode='before')
      def validate_id_fields(cls, value, field_info):
            return validate_id_field(value, field_info.field_name)

class ChatResponse(BaseModel):
    chat_session_id: str
    data: dict

