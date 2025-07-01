
additional_prompt='''Also, User Can Also Provide Additional Prompt: {additional_prompt}. '''
# Define a placeholder for the context (chat history and knowledge context)
general_system_template = """
Answer the question as precisely as possible using the provided Context. 
Context is beloging from user uploaded file so Do not seek clarification regarding the file's origin.
If the human asks for a brief summary of documents or documents information, provide the answer based on the the Context information.Respond to the user's question directly, even if there's no clear context available. Do not apologize or mention that you're unable to provide an answer.
----
Context:
{context}
----------
Chat History:
{chat_history}

----
"""

# Placeholder for the human message template
general_user_template = '''Context:
{context}
Human:```{question}```'''
general_image_template = "{image_url}"
# Placeholder for the AI message template
general_ai_template = "AI Assistant: "  # Example response template


