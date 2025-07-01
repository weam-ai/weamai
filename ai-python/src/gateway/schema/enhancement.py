from typing import Optional
from pydantic import BaseModel, Field,field_validator
from src.gateway.schema.utils import validate_id_field

class EnhanceBase(BaseModel):
      query: str = Field(..., description="The message input by the user to the model.")
      query_id: str = Field(..., description="A unique row identifier for the query id collection, which is defined in MongoDB.")
      company_id: str = Field(...,description="company id required")
      # chat_id: str = Field(..., description="A field in the thread collection indicating the session ID for the chat; it remains the same for the same chat session and changes for new sessions.")
      brain_id: str = Field(..., description="Currently represents a brain name, with plans for it to be represented by a brain ID in the future.")
      user_id:str=Field(..., description="unique idenitfier for idenitfy the user uniqueness")
      code:str=Field("OPEN_AI",description="Code to decide which llm to use for response")
      model_name:Optional[str] = Field(None,description="Name of the Model selected")
      provider:str=Field(None,description="Provider to decide which llm to use for response")
      companymodel: str = Field("companymodel", description="The name of the collection.")
      llm_apikey:str=Field(None,description="company model api key")
      collection_name:str=Field("enhancement",description="enhancement response store table.")

      @field_validator('company_id', 'query_id', mode='before')
      def validate_id_fields(cls, value, field_info):
            return validate_id_field(value, field_info.field_name)
