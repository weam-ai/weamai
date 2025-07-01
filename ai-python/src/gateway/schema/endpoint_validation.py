from pydantic import BaseModel, Field

class EndpointValidationBase(BaseModel):
      token: str = Field("1",description="unique token for huggingface")
      model_repository: str = Field("1", description="Name of the repository of the model")
      model_name: str = Field("companypinecone", description="The Name of the model that is hosted")
      context_length:int = Field(8096,description='The Context length of model selected')