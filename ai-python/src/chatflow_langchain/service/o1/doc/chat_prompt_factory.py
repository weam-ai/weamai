from typing  import Optional
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from src.prompts.langchain.openai.doc_system_prompt import general_system_template,general_ai_template,general_user_template, general_image_template

def create_chat_prompt_doc(general_system_template=general_system_template, general_user_template=general_user_template, general_ai_template=general_ai_template, image_url: Optional[str] = None, additional_prompt: Optional[str] = None):
    messages = [
        HumanMessagePromptTemplate.from_template(general_system_template)]

    if additional_prompt:
        messages.append(HumanMessagePromptTemplate.from_template(additional_prompt))
    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))

    return messages