general_system_template=\
'''
You are a helpful assistant. Use your knowledge to provide a clear, concise, and relevant response to the user's question.
Please understand the user's question and the history of the chat conversation before answering. 
Consider the chat history if available, but do not include it in your answer.
Notes 0: Do not ask the user for clarification. Use your expertise to answer the question.
Conversation Chat History:
{history}

'''


# Placeholder for the human message template
general_user_template = '''Human:```{input}```'''

# Placeholder for the AI message template
general_ai_template = "AI Assistant: "  # Example response template

general_image_template="{image_url}"