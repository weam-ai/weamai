from typing  import Optional
from langchain_core.messages import SystemMessage, HumanMessage
from src.prompts.langchain.pro_agent.qa.qa_special import system_prompt,general_input,system_prompt_page_speed
from src.prompts.langchain.pro_agent.qa.context_prompt import context_system_prompt,context_prompt
from src.logger.default_logger import logger
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate,HumanMessagePromptTemplate
def create_chat_prompt(
    general_system_template=system_prompt, 
    general_user_template=general_input, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    messages = []
    messages.insert(0,SystemMessagePromptTemplate.from_template(general_system_template))
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    chat_prompt = ChatPromptTemplate(messages=messages)
    return chat_prompt  


def create_context_prompt(
    general_system_template=context_system_prompt, 
    general_user_template=context_prompt, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    messages = []
    messages.insert(0,SystemMessagePromptTemplate.from_template(general_system_template))
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    chat_prompt = ChatPromptTemplate(messages=messages)
    return chat_prompt  


def create_chat_prompt_page_speed(
    general_system_template=system_prompt_page_speed, 
    general_user_template=general_input, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    messages = []
    messages.insert(0,SystemMessagePromptTemplate.from_template(general_system_template))
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    chat_prompt = ChatPromptTemplate(messages=messages)
    return chat_prompt