

generic_system_prompt='''
  ----
  Conversation Chat History:
  {chat_history}
  ----
  Context:
  {context}
  -------------   
  Note: User Agent's instructions are optional, whether provided by the user or not.

'''


# Placeholder for the human message template
general_user_question = '''Context:{context}
  Human:```{question}```'''
general_image_template = "{image_url}"
# Placeholder for the AI message template
general_ai_template = "AI Assistant: "  # Example response template

additional_prompt='''Also, User Can Also Provide Additional Prompt: {additional_prompt}. '''
additional_prompt_template='''Also, User Can Also Provide Additional Prompt: {additional_prompt}. '''
