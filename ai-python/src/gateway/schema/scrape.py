from pydantic import BaseModel,Field

class ScrapeRequest(BaseModel):
    # prompt_ids: list = Field(...,description="The identifier for the prompt associated with provided by user if any.")
    promptmodel:str=Field("prompts",description="the name of additional prompt collection")
    companymodel: str = Field("companymodel", description="The name of the collection.")
    company_id: str = Field(...,description="company id required")
    parent_prompt_ids:list=Field(...,description="parent prompt ids where prompt created ")
    child_prompt_ids:list=Field([],description="child prompt ids for add this prompts")
    code:str=Field("OPEN_AI",description="Code to decide which llm to use for response")
    llm_apikey: str = Field(None, description="A unique row identifier for the model collection, specifically referencing gpt-3.5-turbo and other large language models (LLMs).")
    provider:str=Field(None,description="Provider to decide which llm to use for response")
class ScrapeResponse(BaseModel):
    task_chain_id: str
