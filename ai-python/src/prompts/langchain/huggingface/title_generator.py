general_system_template=''' 
Task: Create a Title Generation Algorithm

Requirements:

Entity Identification and Weighting:

Highest Weight: Unique person names in conversation, client names.
Medium Weight: Company names, locations, events.
Lowest Weight: Unique or uncommon terms.

Goal:
Strictly,Generate concise, impactful titles that capture the conversation's unique characteristics by prioritizing entities based on Highest Weight to Lowest Weight while title generating.

Title Generation Constraints:
Length: 8-10 words (strictly enforced).
Content: No special characters allowed.
Priority: Distinctive elements of the conversation take precedence.
Focus: Must succinctly capture the conversation's core essence.

Validation Process:
Ensure the title reflects the primary focus of the conversation.
Confirm clarity and relevance of the title.
Verify adherence to length and character restrictions.

Strictly, title length must be between 8 and 10 words.
Strictly, title only string include don't include any special characters 
Strictly Final Response Format follow the below example and strictly follow ```title``` key for output:
title:xyz
'''

system_template_without_answer='''
Task: Create a Title Generation Algorithm

Requirements:

Entity Identification and Weighting:

Highest Weight: Unique person names in conversation, client names.
Medium Weight: Company names, locations, events.
Lowest Weight: Unique or uncommon terms.

Goal:
Strictly,Generate concise, impactful titles that capture the conversation's unique characteristics by prioritizing entities based on Highest Weight to Lowest Weight while title generating.

Title Generation Constraints:
Length: 8-10 words (strictly enforced).
Content: No special characters allowed.
Priority: Distinctive elements of the conversation take precedence.
Focus: Must succinctly capture the conversation's core essence.

Validation Process:
Ensure the title reflects the primary focus of the conversation.
Confirm clarity and relevance of the title.
Verify adherence to length and character restrictions.

Strictly, title length must be between 8 and 10 words.
Strictly, title only string include don't include any special characters 
Strictly Final Response Format follow the below example and strictly follow ```title``` key for output:
title:xyz
'''
# Placeholder for the human message template
general_user_template = '''User Query:{question}'''

 
# Placeholder for the AI message template
general_ai_template = """AI Answer:{answer}
The preceding text is a conversation thread that needs a concise but descriptive 8 to 10 word title in natural English so that readers will be able to easily find it again. Do not add any quotation marks or formatting to the title. Respond only with the title text.
"""  # Example response template