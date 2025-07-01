from typing import Optional,List,Union
from pydantic import BaseModel, Field,field_validator
from src.gateway.schema.utils import validate_id_field
from pydantic import BaseModel, Extra



class ExtraFilePayload(BaseModel):
      """
      Represents a request to process text data, embed it with OpenAI, and store it in a vector database.

      This class defines the parameters required to process text data using OpenAI and store the results in a Qdrant
      vector database.

      Attributes:
      - `id` (str): A unique identifier for the request.
      - `tag` (str): A tag for categorization or identification of the request.
      """

      id: str = Field(..., description="File id which belongs to MongoDB.")
      tag: str = Field(..., description="File tag id or list of tags.")

      @field_validator('id', mode='before')
      def validate_id_fields(cls, value, field_info):
            return validate_id_field(value, field_info.field_name)

class CustomGPTChatBase(BaseModel):
      thread_id: str = Field(..., description="A unique row identifier for the thread collection, which is defined in MongoDB.")
      custom_gpt_id:str=Field(...,descitpion="Id of Custom GPT ")
      company_id: str = Field(...,description="company id required")
      query: str = Field(..., description="The message input by the user to the model.")
      chat_session_id: str = Field(..., description="A field in the thread collection indicating the session ID for the chat; it remains the same for the same chat session and changes for new sessions.")
      prompt_id: Optional[str] = Field(default=None,description="The identifier for the additional prompt associated with provided by user if any.")
      llm_apikey: str = Field(..., description="A unique row identifier for the model collection, specifically referencing gpt-3.5-turbo and other large language models (LLMs).")
      companymodel: str = Field("companymodel", description="The name of the collection.")
      threadmodel: str = Field("messages", description="The name of the collection.")
      promptmodel:str=Field("prompts",description="the name of additional prompt collection")
      customgptmodel:str=Field("customgpt",description="the name of custom gpt")
      delay_chunk:float=Field(0.3,description="chunk delay response flag")
      image_url:Optional[Union[str, list[str]]]=Field(None,description="image_url pass for analysis")
      isregenerated:bool=Field(False,description="Flag for regeneration")
      code:str=Field("OPEN_AI",description="Code to decide which llm to use for response")
      model_name:Optional[str] = Field(None,description="Name of the Model selected")
      chat_docs_collection:str=Field("chatdocs",description="chat docs collection")
      provider:str=Field(None,description="Provider to decide which llm to use for response")
      file_id:Optional[Union[str, list[str]]] = Field(None, description="A unique row identifier for a file collection, which is defined in MongoDB.")
      tag: Optional[Union[str, list[str]]] = Field(None, description="The name of the file, which is stored in the file collection as name.")
      msgCredit:Optional[float]=Field(0,description="Message Credit")
      is_paid_user:bool=Field(True,description='Plan Type Flag')
      class Config:
        extra = Extra.allow  # or simply: extra = 'allow'
      @field_validator('company_id', 'thread_id','custom_gpt_id', 'chat_session_id', mode='before')
      def validate_id_fields(cls, value, field_info):
            return validate_id_field(value, field_info.field_name)
     



class CustomGPTDocChatBase(CustomGPTChatBase):
      companypinecone: str = Field("companypinecone", description="The name of the companypinecone collection, which is defined in MongoDB.")
      isMedia:bool=Field(True,description="flag of media using")