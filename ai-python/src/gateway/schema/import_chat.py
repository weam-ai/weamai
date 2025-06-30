from pydantic import BaseModel, Field

class ImportChatBase(BaseModel):
      user_id: str = Field(..., description="user_id.")
      company_id: str = Field(...,description="company id required")
      brain_id: str = Field(...,description="brain id .")
      brain_title: str = Field(...,description="brain title.")
      brain_slug: str = Field(...,description="brain slug.")
      company_name: str = Field(...,description="company name.")
      companymodel: str = Field("companymodel", description="The name of the collection.")
class ImportChatJsonBase(BaseModel):
      user_id: str = Field(..., description="user_id.")
      company_id: str = Field(...,description="company id required")
      brain_id: str = Field(...,description="brain id .")
      brain_title: str = Field(...,description="brain title.")
      brain_slug: str = Field(...,description="brain slug.")
      company_name: str = Field(...,description="company name.")
      companymodel: str = Field("companymodel", description="The name of the collection.")
      code: str = Field(...,description="Import chat resource code.")