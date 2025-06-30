from typing  import Optional
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from src.prompts.langchain.llama.simple_system_prompt import general_system_template,general_user_template,general_ai_template,general_image_template
from src.logger.default_logger import logger

def create_chat_prompt_doc(
    general_system_template=general_system_template, 
    general_user_template=general_user_template, 
    general_ai_template=general_ai_template, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template)
    ]
    
    if additional_prompt:
        messages.append(HumanMessagePromptTemplate.from_template(additional_prompt))
    
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    
    messages.append(AIMessagePromptTemplate.from_template(general_ai_template))

    qa_prompt = ChatPromptTemplate.from_messages(messages)
    logger.info("Created chat prompt document.")
    return qa_prompt


def create_chat_prompt_doc_image(
    general_system_template=general_system_template, 
    general_user_template=general_user_template, 
    general_ai_template=general_user_template, 
    general_image_template=general_image_template, 
    additional_prompt: Optional[str] = None, 
    **kwargs
):
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template)
    ]
    
    if additional_prompt:
        messages.append(HumanMessagePromptTemplate.from_template(additional_prompt))
    
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    
    messages.extend([
        HumanMessagePromptTemplate.from_template(template=[{"type": "image_url", "image_url": {"url": general_image_template, "detail": "high"}}]),
        AIMessagePromptTemplate.from_template(general_ai_template)
    ])

    qa_prompt = ChatPromptTemplate.from_messages(messages)
    logger.info("Created chat prompt document image.")
    return qa_prompt