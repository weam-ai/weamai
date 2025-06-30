from typing  import Optional
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from src.logger.default_logger import logger

from src.prompts.langchain.llama.doc_system_prompt import general_system_template,general_ai_template,general_user_template
def create_chat_prompt_doc(chat_history:str,general_system_template=general_system_template, general_user_template=general_user_template, general_ai_template=general_ai_template, additional_prompt: Optional[str] = None) -> ChatPromptTemplate:
        """
        Creates a chat prompt document using the provided templates and user-specific prompts.
        
        Args:
            generic_system_prompt (str): The generic system prompt template.
            general_user_question (str): The generic user question template.
            general_ai_template (str): The generic AI response template.
            additional_prompt (Optional[str]): An additional prompt to include in the chat template.
        
        Returns:
            ChatPromptTemplate: The generated chat prompt template.
        """
        messages = [
            SystemMessagePromptTemplate.from_template(general_system_template)]
        

        if additional_prompt:
            messages.append(HumanMessagePromptTemplate.from_template(additional_prompt))
        
        chat_history.append(HumanMessagePromptTemplate.from_template(general_user_template))
        # messages.append(AIMessagePromptTemplate.from_template(general_ai_template))
        # messages.extend(
        #     HumanMessagePromptTemplate.from_template(general_user_question),
        #     AIMessagePromptTemplate.from_template(general_ai_template)
        # )

        qa_prompt = ChatPromptTemplate.from_messages(chat_history)
        logger.info("Created chat prompt document.")
        return qa_prompt

