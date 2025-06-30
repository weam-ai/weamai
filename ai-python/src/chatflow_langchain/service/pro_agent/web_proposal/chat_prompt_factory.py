from typing  import Optional
from langchain_core.messages import SystemMessage, HumanMessage
from src.prompts.langchain.pro_agent.web_proposal.web_proposal_prompt import system_proposal_prompt,general_proposal_input,general_requirements_input,general_company_summary_input,general_company_summary_prompt
from src.logger.default_logger import logger
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate,HumanMessagePromptTemplate
def create_chat_prompt_proposal(
    general_system_template=system_proposal_prompt, 
    general_user_template=general_proposal_input, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    messages = []
    messages.insert(0,SystemMessagePromptTemplate.from_template(general_system_template))
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    chat_prompt = ChatPromptTemplate(messages=messages)
    return chat_prompt  

def create_chat_prompt_requirements(
    general_system_template=system_proposal_prompt, 
    general_user_template=general_requirements_input, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    messages = []
    messages.insert(0,SystemMessagePromptTemplate.from_template(general_system_template))
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    chat_prompt = ChatPromptTemplate(messages=messages)
    return chat_prompt  
    
def create_chat_prompt_company_summary(
    general_system_template=general_company_summary_prompt, 
    general_user_template=general_company_summary_input, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    messages = []
    messages.insert(0,SystemMessagePromptTemplate.from_template(general_system_template))
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    chat_prompt = ChatPromptTemplate(messages=messages)
    return chat_prompt