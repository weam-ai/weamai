from pydantic import BaseModel, Field

class QdrantIndexBase(BaseModel):
      company_id: str = Field("1",description="unique id of company mongodb document id")
      qdrant_apikey_id: str = Field("1", description="A unique row identifier for the companypinecone collection, which is defined in MongoDB.")
      companypinecone: str = Field("companypinecone", description="The name of the companypinecone collection, which is defined in MongoDB.")
    