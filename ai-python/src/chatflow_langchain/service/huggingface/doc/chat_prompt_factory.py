from typing  import Optional
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from src.prompts.langchain.huggingface.doc_system_prompt import general_system_template,general_ai_template,general_user_template

def create_chat_prompt_doc(general_system_template=general_system_template, general_user_template=general_user_template, general_ai_template=general_ai_template, additional_prompt: Optional[str] = None):
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template)]

    if additional_prompt:
        messages.append(HumanMessagePromptTemplate.from_template(additional_prompt))

    messages.append(HumanMessagePromptTemplate.from_template(general_user_template))
    # messages.append(AIMessagePromptTemplate.from_template(general_ai_template))
      

    qa_prompt = ChatPromptTemplate.from_messages(messages)
    return qa_prompt



