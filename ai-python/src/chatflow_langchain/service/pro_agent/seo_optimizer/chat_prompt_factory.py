from typing  import Optional
from langchain_core.messages import SystemMessage, HumanMessage
from src.prompts.langchain.pro_agent.seo_optimizer.summary_prompt import system_prompt,summary_prompt,audience_prompt
from src.prompts.langchain.pro_agent.seo_optimizer.topic_gen_prompt import system_prompt_topic,topic_prompt
from src.prompts.langchain.pro_agent.seo_optimizer.article_gen_prompt import system_article_prompt,article_prompt
from src.logger.default_logger import logger
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate,HumanMessagePromptTemplate
def create_prompt_summary(
    general_system_template=system_prompt, 
    general_user_template=summary_prompt, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    messages = []
    messages.insert(0,SystemMessagePromptTemplate.from_template(general_system_template))
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    chat_prompt = ChatPromptTemplate(messages=messages)
    return chat_prompt  


def create_prompt_audience(
    general_system_template=system_prompt, 
    general_user_template=audience_prompt, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    messages = []
    messages.insert(0,SystemMessagePromptTemplate.from_template(general_system_template))
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    chat_prompt = ChatPromptTemplate(messages=messages)
    return chat_prompt  

def create_prompt_topic(
    general_system_template=system_prompt_topic, 
    general_user_template=topic_prompt, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    """
    Create a chat prompt for generating content topics.
    
    Args:
        general_system_template (str): System message template.
        general_user_template (str): User message template.
        additional_prompt (Optional[str]): Additional input to enhance the prompt.
    
    Returns:
        ChatPromptTemplate: A formatted chat prompt template.
    """
    messages = []
    messages.insert(0, SystemMessagePromptTemplate.from_template(general_system_template))
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    
    if additional_prompt:
        messages.append(HumanMessagePromptTemplate.from_template(additional_prompt))
    
    chat_prompt = ChatPromptTemplate(messages=messages)
    return chat_prompt



def create_prompt_article(
    general_system_template=system_article_prompt, 
    general_user_template=article_prompt, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):  
    """
    Create a chat prompt for generating content topics or articles.
    
    This function constructs a chat prompt template by combining system and user message templates,
    and optionally appending additional prompt instructions provided by the user.
    
    Args:
        general_system_template (str): The template for the system message (e.g., system-level instructions or context).
        general_user_template (str): The template for the user message (initial instruction or request).
        additional_prompt (Optional[str]): An optional additional instruction or user input to further refine the prompt.
        **kwargs: Additional arguments that can be passed for future extensibility.
    
    Returns:
        ChatPromptTemplate: A compiled chat prompt containing the system message, user message, 
        and any optional additional instructions, ready to be used for generating AI-driven content.
    """
    messages = []
    messages.insert(0, SystemMessagePromptTemplate.from_template(general_system_template))
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    
    if additional_prompt:
        messages.append(HumanMessagePromptTemplate.from_template(additional_prompt))
    
    chat_prompt = ChatPromptTemplate(messages=messages)
    return chat_prompt