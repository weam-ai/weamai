from typing import Optional
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Import custom templates
from src.prompts.langchain.gemini.custom_gpt.simple_system_prompt import general_ai_template, general_user_question, generic_system_prompt,general_image_template
from src.logger.default_logger import logger

class UserCustomGPTPrompt:
    """
    A class to create custom user GPT prompts for a chat system.
    """

    def initialization(self, user_agent_name: str, user_system_prompt: str, user_goals: str, user_instructions: str):
        """
        Initializes the UserCustomGPTPrompt with user-specific details.
        
        Args:
            user_agent_name (str): The name of the user agent.
            user_system_prompt (str): The system prompt for the user agent.
            user_goals (str): The goals of the user agent.
            user_instructions (str): Specific instructions for the user agent.
        """
        self.user_agent_name = user_agent_name
        self.user_system_prompt = user_system_prompt
        self.user_goals = user_goals
        self.user_instructions = user_instructions

    def get_user_system_prompt(self) -> str:
        """
        Generates the user system prompt using the provided details.
        
        Returns:
            str: The formatted user system prompt.
        """
        general_user_system_template = '''
        ----
        User Agent's Name:
        {user_agent_name}
        -----
        User Agent's System Prompt:
        {user_system_prompt}
        --------
        User Agent's Goals :
        {user_goals}
        ------------
        User Agent's Instructions:
        {user_instructions}
        -------------------------
        '''
        return general_user_system_template.format(
            user_agent_name=self.user_agent_name,
            user_system_prompt=self.user_system_prompt,
            user_goals=self.user_goals,
            user_instructions=self.user_instructions
        )

    def create_chat_prompt(self, generic_system_prompt: str = generic_system_prompt, general_user_question: str = general_user_question, 
                               general_ai_template: str = general_ai_template, additional_prompt: Optional[str] = None) -> ChatPromptTemplate:
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
        user_system_message = self.get_user_system_prompt()
        messages = [
            SystemMessagePromptTemplate.from_template(user_system_message),
            SystemMessagePromptTemplate.from_template(generic_system_prompt)]

        if additional_prompt:
            messages.append(HumanMessagePromptTemplate.from_template(additional_prompt))
        
        messages.append(HumanMessagePromptTemplate.from_template(general_user_question))
        # messages.append(AIMessagePromptTemplate.from_template(general_ai_template))
        # messages.extend(
        #     HumanMessagePromptTemplate.from_template(general_user_question),
        #     AIMessagePromptTemplate.from_template(general_ai_template))
            
    

        qa_prompt = ChatPromptTemplate.from_messages(messages)
        logger.info("Created chat prompt.")
        return qa_prompt
    
    def create_chat_prompt_image(self, generic_system_prompt: str = generic_system_prompt, general_user_question: str = general_user_question, 
                               general_ai_template: str = general_ai_template, additional_prompt: Optional[str] = None) -> ChatPromptTemplate:
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
        user_system_message = self.get_user_system_prompt()
        messages = [
            SystemMessagePromptTemplate.from_template(user_system_message),
            SystemMessagePromptTemplate.from_template(generic_system_prompt)]

        if additional_prompt:
            messages.append(HumanMessagePromptTemplate.from_template(additional_prompt))
        
        messages.append(HumanMessagePromptTemplate.from_template(general_user_question))
        
        # messages.append(AIMessagePromptTemplate.from_template(general_ai_template))
        # messages.extend(
        #     HumanMessagePromptTemplate.from_template(general_user_question),\
        #     HumanMessagePromptTemplate.from_template(template=[{"type":"image_url","image_url":{"url":general_image_template}}]),
        #     AIMessagePromptTemplate.from_template(general_ai_template)
        #     )

        # qa_prompt = ChatPromptTemplate.from_messages(messages)
        logger.info("Created chat prompt image.")
        return messages


# Example usage:
# user_prompt = UserCustomGPTPrompt()
# user_prompt.initialization(
#     user_agent_name="ChatGPT Helper",
#     user_system_prompt="Assist with generating user-specific prompts.",
#     user_goals="Provide accurate and helpful responses.",
#     user_instructions="Follow the user instructions and provide detailed answers."
# )


# chat_prompt_doc = user_prompt.create_chat_prompt_doc(
#     generic_system_prompt="This is the general system prompt.",
#     general_user_question="This is the general user question.",
#     general_ai_template="This is the general AI template.",
#     additional_prompt="This is an additional prompt."
# )


# Example usage:
# user_prompt = UserCustomGPTPrompt()
# user_prompt.initialization(
#     user_agent_name="ChatGPT Helper",
#     user_system_prompt="Assist with generating user-specific prompts.",
#     user_goals="Provide accurate and helpful responses.",
#     user_instructions="Follow the user instructions and provide detailed answers."
# )


# chat_prompt_doc = user_prompt.create_chat_prompt_doc(
#     generic_system_prompt="This is the general system prompt.",
#     general_user_question="This is the general user question.",
#     general_ai_template="This is the general AI template.",
#     additional_prompt="This is an additional prompt."
# )

