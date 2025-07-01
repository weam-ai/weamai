from typing  import Optional
from langchain_core.messages import SystemMessage, HumanMessage
from src.prompts.langchain.pro_agent.sales_analyzer.sales_analyzer_prompt import system_prompt,general_input,system_with_url_prompt,user_input,user_input_url
from src.logger.default_logger import logger
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate,HumanMessagePromptTemplate
def create_chat_prompt_with_url(
    user_prompt:str=None,
    general_system_template=system_with_url_prompt, 
    general_user_template=general_input, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    messages = []
    if user_prompt is None:
        messages.insert(0,SystemMessagePromptTemplate.from_template(general_system_template))
        messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    else:
        messages.insert(0,SystemMessagePromptTemplate.from_template(user_prompt))
        messages.append(HumanMessagePromptTemplate.from_template(user_input_url))
    chat_prompt = ChatPromptTemplate(messages=messages)
    return chat_prompt  


def create_chat_prompt(
    user_prompt:str=None,
    general_system_template=system_prompt, 
    general_user_template=general_input, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    messages = []
    if user_prompt is None:
        messages.insert(0,SystemMessagePromptTemplate.from_template(general_system_template))
        messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    else:
        messages.insert(0,SystemMessagePromptTemplate.from_template(user_prompt))
        messages.append(HumanMessagePromptTemplate.from_template(user_input))
    chat_prompt = ChatPromptTemplate(messages=messages)
    return chat_prompt  