from typing  import Optional
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from src.prompts.langchain.openai.image.image_prompt import general_system_template,general_user_template,general_ai_template

class ImagePrompt:
    def initialization(self,general_system_template=general_system_template,general_user_template=general_user_template,general_ai_template=general_ai_template):
        self.general_system_template=general_system_template
        self.general_user_template = general_user_template
        self.general_ai_template = general_ai_template

    def create_chat_prompt_image(self, additional_prompt: Optional[str] = None,**kwargs):
        messages = [
            SystemMessagePromptTemplate.from_template(self.general_system_template),
            HumanMessagePromptTemplate.from_template(self.general_user_template),
            AIMessagePromptTemplate.from_template(self.general_ai_template)
        ]

        if additional_prompt:
            messages.append(SystemMessagePromptTemplate.from_template(additional_prompt))

        qa_prompt = ChatPromptTemplate.from_messages(messages)
        return qa_prompt