from typing  import Optional
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from src.prompts.langchain.huggingface.canvas_prompt import general_system_template,\
    general_user_template,general_ai_template,general_system_template_with_code,general_system_template_doc, \
general_system_template_customgpt,general_system_template_customgptDoc
from src.prompts.langchain.huggingface.canvas_prompt import openai_tool_prompt_template,customgpt_doc_prompt_template,customgpt_tool_prompt_template,doc_tool_prompt_template
from src.logger.default_logger import logger


def create_chat_prompt_canvas(general_system_template=openai_tool_prompt_template, general_user_template=general_user_template, general_ai_template=general_ai_template, additional_prompt: Optional[str] = None):
    canvas_prompt_list = [
        SystemMessage(general_system_template),
        HumanMessage(general_user_template),
    ]
    logger.info("Created chat prompt canvas.")
    return canvas_prompt_list

def chat_prompt_with_code_canvas(general_system_template=general_system_template_with_code, general_user_template=general_user_template, general_ai_template=general_ai_template, additional_prompt: Optional[str] = None):
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template),
        HumanMessagePromptTemplate.from_template(general_user_template),
        AIMessagePromptTemplate.from_template(general_ai_template)
    ]
    canvas_prompt = ChatPromptTemplate.from_messages(messages)
    logger.info("Created chat prompt canvas.")
    return canvas_prompt


def chat_prompt_with_doc_canvas(general_system_template=doc_tool_prompt_template, general_user_template=general_user_template, general_ai_template=general_ai_template, additional_prompt: Optional[str] = None):
    canvas_prompt_list = [
        SystemMessage(general_system_template),
        HumanMessage(general_user_template),
    ]
    logger.info("Created chat prompt canvas for Doc.")
    return canvas_prompt_list



def chat_prompt_with_customgpt(general_system_template=customgpt_tool_prompt_template, general_user_template=general_user_template, general_ai_template=general_ai_template, additional_prompt: Optional[str] = None):
    canvas_prompt_list = [
        SystemMessage(general_system_template),
        HumanMessage(general_user_template),
    ]
    logger.info("Created chat prompt canvas for CustomGPT.")
    return canvas_prompt_list

def chat_prompt_with_customgpt_doc(general_system_template=customgpt_doc_prompt_template, general_user_template=general_user_template, general_ai_template=general_ai_template, additional_prompt: Optional[str] = None):
    canvas_prompt_list = [
        SystemMessage(general_system_template),
        HumanMessage(general_user_template),
    ]
    logger.info("Created chat prompt canvas for CustomGPT.")
    return canvas_prompt_list