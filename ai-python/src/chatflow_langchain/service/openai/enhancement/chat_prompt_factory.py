from typing  import Optional
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from src.prompts.langchain.openai.query_enhancer import general_system_template,general_user_template,general_ai_template
from src.logger.default_logger import logger


def chat_prompt_query_enhance(general_system_template=general_system_template, general_user_template=general_user_template, general_ai_template=general_ai_template, additional_prompt: Optional[str] = None):
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template),
        HumanMessagePromptTemplate.from_template(general_user_template),
    ]

    qa_prompt = ChatPromptTemplate.from_messages(messages)
    logger.info("Created chat prompt title.")
    return qa_prompt

