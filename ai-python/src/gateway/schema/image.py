from typing import Optional
from pydantic import BaseModel, Field
class ImageGenerateConfig(BaseModel):
    DALLE_WRAPPER_SIZE: str = Field(default="1024x1024")
    DALLE_WRAPPER_QUALITY: str = Field(default='standard')
    DALLE_WRAPPER_STYLE: str = Field(default='vivid')
    def to_dict(self):
        return self.dict()

class ImageBase(BaseModel):
      thread_id: str = Field(..., description="A unique row identifier for the thread collection, which is defined in MongoDB.")
      company_id: str = Field(...,description="company id required")
      prompt_id: Optional[str] = Field(default=None,description="The identifier for the additional prompt associated with provided by user if any.")
      query: str = Field(..., description="The message input by the user to the model.")
      llm_apikey: str = Field(..., description="A unique row identifier for the model collection, specifically referencing gpt-3.5-turbo and other large language models (LLMs).")
      chat_session_id: str = Field(..., description="A field in the thread collection indicating the session ID for the chat; it remains the same for the same chat session and changes for new sessions.")
      companymodel: str = Field("companymodel", description="The name of the collection.")
      threadmodel: str = Field("messages", description="The name of the collection.")
      promptmodel:str=Field("prompts",description="the name of additional prompt collection")
      extraconfig: dict = Field(None, description="Extra Configuration of the DALL-E initialization")
      dalle_wrapper_size:str = Field('1024x1024', description="Size Configuration for the dalle model")
      dalle_wrapper_quality:str = Field('standard', description="quality Configuration for the dalle model.")
      dalle_wrapper_style:str = Field('vivid', description="style Configuration for the dalle model.")
      delay_chunk:float=Field(0.3,description="chunk delay response flag")