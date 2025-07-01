from typing import Optional, List
from pydantic import BaseModel, HttpUrl,Field, field_validator


class ProAgentRequestSchema(BaseModel):
    pro_agent_code: str=Field(...,description="The code of the pro agent")
    pro_agent_id: str=Field("123",description="The id of the pro agent")
    query: str=Field(...,description="The query of the pro agent")
    agent_extra_info: dict=Field({},description="The payload of the pro agent")
    thread_id: str=Field(...,description="The thread id of the pro agent")
    company_id: str=Field(...,description="The company id of the pro agent")
    chat_session_id: str=Field(...,description="The chat id of the pro agent")
    brain_id: str=Field(...,description="The brain id of the pro agent")
    delay_chunk:float=Field(0.01,description="chunk delay response flag")
    companymodel: str = Field("companymodel", description="The name of the collection.")
    threadmodel: str=Field("messages",description="The chat collection name of the pro agent")
    isregenerated: bool=Field(False,description="The regenerate flag of the pro agent")
    msgCredit:Optional[float]=Field(0,description="Message Credit")
    is_paid_user:bool=Field(True,description='Plan Type Flag')

class ProSalesCallAnalyzerSchema(BaseModel):
    pro_agent_code: str=Field(...,description="The code of the pro agent")
    pro_agent_id: str=Field("123",description="The id of the pro agent")
    query: str=Field(...,description="The query of the pro agent")
    agent_extra_info: dict=Field({},description="The payload of the pro agent")
    thread_id: str=Field(...,description="The thread id of the pro agent")
    company_id: str=Field(...,description="The company id of the pro agent")
    chat_session_id: str=Field(...,description="The chat id of the pro agent")
    delay_chunk:float=Field(0.01,description="chunk delay response flag")
    companymodel: str = Field("companymodel", description="The name of the collection.")
    threadmodel: str=Field("messages",description="The chat collection name of the pro agent")
    isregenerated: bool=Field(False,description="The regenerate flag of the pro agent")
    msgCredit:Optional[float]=Field(0,description="Message Credit")
    is_paid_user:bool=Field(True,description='Plan Type Flag')
    service_code:str=Field(...,description="The service code of the pro agent")
    product_summary_code:str=Field(...,description="The product code of the pro agent")
    

class ProSEOKeywordRequestSchema(BaseModel):
    pro_agent_code: str=Field(...,description="The code of the pro agent")
    pro_agent_id: str=Field("123",description="The id of the pro agent")
    query: str=Field(...,description="The query of the pro agent")
    agent_extra_info: dict=Field({},description="The payload of the pro agent")
    thread_id: str=Field(...,description="The thread id of the pro agent")
    company_id: str=Field(...,description="The company id of the pro agent")
    chat_session_id: str=Field(...,description="The chat id of the pro agent")
    brain_id: str=Field(...,description="The brain id of the pro agent")
    delay_chunk:float=Field(0.01,description="chunk delay response flag")
    companymodel: str = Field("companymodel", description="The name of the collection.")
    threadmodel: str=Field("messages",description="The chat collection name of the pro agent")
    isregenerated: bool=Field(False,description="The regenerate flag of the pro agent")
    msgCredit:Optional[float]=Field(0,description="Message Credit")
    is_paid_user:bool=Field(True,description='Plan Type Flag')

    @field_validator("agent_extra_info")
    @classmethod
    def validate_agent_extra_info(cls, v):
        expected = {
            "project_name": str,
            "location": list,
            "target_keywords": list,
            "language": str,
            "website_url": str,
            "business_summary": str,
            "target_audience": str,
        }

        provided_fields = list(v.keys())
        if not isinstance(v, dict):
            raise TypeError("agent_extra_info must be a dictionary.")

        for key, expected_type in expected.items():
            if key not in v:
                raise ValueError(f"Missing field: '{key}' and Provided fields: {provided_fields}")
            value = v[key]

            if expected_type == list:
                if isinstance(value, str):
                    raise ValueError(f"agent_extra_info is invalid: '{key}' must be of type list where it's getting type str. Provided value: '{value}'.")
                
                if not isinstance(value, list):
                    raise ValueError(f"agent_extra_info is invalid: '{key}' must be of type list where it's getting type {type(value).__name__}. Provided value: '{value}'.")

                if not all(isinstance(i, str) for i in value):
                    raise ValueError(f"agent_extra_info is invalid: All items in '{key}' must be strings. Provided value: {value}")
            else:
                if not isinstance(value, expected_type):
                    raise ValueError(f"agent_extra_info is invalid: '{key}' must be of type {expected_type.__name__} where it's getting type {type(value).__name__}. Provided value: {value}")

        extras = set(v.keys()) - set(expected.keys())
        if extras:
            raise ValueError(f"agent_extra_info is invalid: Unexpected fields in agent_extra_info: {', '.join(extras)}")
        return v

class ProSEOSummaryRequestSchema(BaseModel):
    pro_agent_code: str=Field(...,description="The code of the pro agent")
    pro_agent_id: str=Field("123",description="The id of the pro agent")
    query: str=Field(None,description="The query of the pro agent")
    agent_extra_info: dict=Field({},description="The payload of the pro agent")
    company_id: str=Field(...,description="The company id of the pro agent")
    delay_chunk:float=Field(0.01,description="chunk delay response flag")
    companymodel: str = Field("companymodel", description="The name of the collection.")
    threadmodel: str=Field("seoSummaries",description="The chat collection name of the pro agent")
    isregenerated: bool=Field(False,description="The regenerate flag of the pro agent")
    msgCredit:Optional[float]=Field(0,description="Message Credit")
    is_paid_user:bool=Field(True,description='Plan Type Flag')

    @field_validator("agent_extra_info")
    @classmethod
    def validate_agent_extra_info(cls, v):
        expected = {
            "project_name": str,
            "location": list,
            "target_keywords": list,
            "language": str,
            "website_url": str,
        }

        provided_fields = list(v.keys())
        if not isinstance(v, dict):
            raise TypeError("agent_extra_info must be a dictionary.")

        for key, expected_type in expected.items():
            if key not in v:
                raise ValueError(f"agent_extra_info is invalid: Missing field: '{key}'. Provided fields: {provided_fields}")
            
            value = v[key]

            if expected_type == list:
                if isinstance(value, str):
                    raise ValueError(f"agent_extra_info is invalid: '{key}' must be of type list where it's getting type str. Provided value: '{value}'|")
                
                if not isinstance(value, list):
                    raise ValueError(f"agent_extra_info is invalid: '{key}' must be of type list where it's getting type {type(value).__name__}. Provided value: '{value}'.")

                if not all(isinstance(i, str) for i in value):
                    raise ValueError(f"agent_extra_info is invalid: All items in '{key}' must be strings. Provided value: {value}")
            else:
                if not isinstance(value, expected_type):
                    raise ValueError(f"agent_extra_info is invalid: '{key}' must be of type {expected_type.__name__} where it's getting type {type(value).__name__}. Provided value: {value}")

        extras = set(provided_fields) - set(expected.keys())
        if extras:
            raise ValueError(f"agent_extra_info is invalid: Unexpected fields in agent_extra_info: {', '.join(extras)}")

        return v

class ProSEOTopicRequestSchema(BaseModel):
    pro_agent_code: str=Field(...,description="The code of the pro agent")
    pro_agent_id: str=Field("123",description="The id of the pro agent")
    thread_id: str=Field(...,description="The thread id of the pro agent")
    company_id: str=Field(...,description="The company id of the pro agent")
    companymodel: str = Field("companymodel", description="The name of the collection.")
    # chat_session_id: str=Field(...,description="The chat id of the pro agent")
    # brain_id: str=Field(...,description="The brain id of the pro agent")
    delay_chunk:float=Field(0.01,description="chunk delay response flag")
    threadmodel: str=Field("messages",description="The chat collection name of the pro agent")
    isregenerated: bool=Field(False,description="The regenerate flag of the pro agent")
    msgCredit:Optional[float]=Field(0,description="Message Credit")
    is_paid_user:bool=Field(True,description='Plan Type Flag')
    agent_extra_info: dict=Field({},description="The payload of the pro agent")

    @field_validator("agent_extra_info")
    @classmethod
    def validate_agent_extra_info(cls, v):
        if not isinstance(v, dict):
            raise ValueError("agent_extra_info must be a dictionary")

        if "primary_keywords" not in v:
            raise ValueError("agent_extra_info must include 'primary_keywords'")
        if not v["primary_keywords"]:
            raise ValueError("'primary_keywords' list must not be empty")
        if not isinstance(v["primary_keywords"], list):
            raise ValueError("'primary_keywords' must be a list")
        if not all(isinstance(item, str) for item in v["primary_keywords"]):
            raise ValueError("All items in 'primary_keywords' must be strings")
        
        if "secondary_keywords" not in v:
            raise ValueError("agent_extra_info must include 'secondary_keywords'")
        if not v["secondary_keywords"]:
            raise ValueError("'secondary_keywords' list must not be empty")
        if not isinstance(v["secondary_keywords"], list):
            raise ValueError("'secondary_keywords' must be a list")
        if not all(isinstance(item, str) for item in v["secondary_keywords"]):
            raise ValueError("All items in 'secondary_keywords' must be strings")


        return v


class ProSEOArticleRequestSchema(BaseModel):
    pro_agent_code: str=Field(...,description="The code of the pro agent")
    pro_agent_id: str=Field("123",description="The id of the pro agent")
    thread_id: str=Field(...,description="The thread id of the pro agent")
    company_id: str=Field(...,description="The company id of the pro agent")
    companymodel: str = Field("companymodel", description="The name of the collection.")
    # chat_session_id: str=Field(...,description="The chat id of the pro agent")
    # brain_id: str=Field(...,description="The brain id of the pro agent")
    delay_chunk:float=Field(0.01,description="chunk delay response flag")
    threadmodel: str=Field("messages",description="The chat collection name of the pro agent")
    isregenerated: bool=Field(False,description="The regenerate flag of the pro agent")
    msgCredit:Optional[float]=Field(0,description="Message Credit")
    is_paid_user:bool=Field(True,description='Plan Type Flag')
    agent_extra_info: dict=Field({},description="The payload of the pro agent")


    @field_validator("agent_extra_info")
    @classmethod
    def validate_agent_extra_info(cls, v):
        if not isinstance(v, dict):
            raise ValueError("agent_extra_info must be a dictionary")

        if "topics" not in v:
            raise ValueError("agent_extra_info must include 'topics'")

        if not isinstance(v["topics"], str):
            raise ValueError("'topics' must be a string")

        if not v["topics"].strip():
            raise ValueError("'topics' must not be empty")

        return v







class ProVideoAnalysisRequestSchema(BaseModel):
    pro_agent_code: str=Field(...,description="The code of the pro agent")
    pro_agent_id: str=Field("123",description="The id of the pro agent")
    agent_extra_info: dict=Field({},description="The payload of the pro agent")
    company_id: str=Field(...,description="The company id of the pro agent")
    delay_chunk:float=Field(0.01,description="chunk delay response flag")
    companymodel: str = Field("companymodel", description="The name of the collection.")
    file_collection: str=Field("file",description="The chat collection name of the pro agent")
