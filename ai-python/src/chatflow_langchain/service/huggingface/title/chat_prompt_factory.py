from typing  import Optional
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from src.prompts.langchain.huggingface.title_generator import general_system_template,general_user_template,general_ai_template,system_template_without_answer
from src.logger.default_logger import logger

def create_chat_prompt_title(general_system_template=general_system_template, general_user_template=general_user_template, general_ai_template=general_ai_template, additional_prompt: Optional[str] = None):
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template),
        HumanMessagePromptTemplate.from_template(general_user_template),
        HumanMessagePromptTemplate.from_template(general_ai_template)
    ]

    qa_prompt = ChatPromptTemplate.from_messages(messages)
    logger.info("Created chat prompt title.")
    return qa_prompt

def prompt_title_without_answer(general_system_template=system_template_without_answer, general_user_template=general_user_template, additional_prompt: Optional[str] = None):
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template),
        HumanMessagePromptTemplate.from_template(general_user_template),
    ]

    qa_prompt = ChatPromptTemplate.from_messages(messages)
    logger.info("Created chat prompt title.")
    return qa_prompt