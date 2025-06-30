import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Simple Chat Shuffled payloads

# # Base payload
TOOL_CHAT = {
    "thread_id": "66f13702036f40815a44bc38",
    "query": "hello",
    "llm_apikey": "66f12266036f40815a44bb4d",
    "chat_session_id": "66f136bb036f40815a44bc1d",
    "company_id": "66e1244ba6344e751faf730c",
    "delay_chunk": 0.02
}

# List of variations for the "query" field
query_variations = [
    "get me list of tools",
    "latest news",
    "how to use the tool",
    "provide details on the tool",
    "give me an overview of the tool"
]

# Function to generate shuffled payloads
def generate_payloads(base_payload, variations):
    payloads = []
    for query in variations:
        new_payload = base_payload.copy()  # Copy the base payload
        new_payload["query"] = query  # Set the new query
        payloads.append(new_payload)  # Add the new payload to the list
    return payloads

# Generate shuffled payloads
shuffled_payloads = generate_payloads(TOOL_CHAT, query_variations)


# CHAT + IMAGE Shuffled Payloads

# custom_query_variations = [
#     "get me list of tools",                     # Chat
#     "latest news",                              # Chat
#     "make a digital portrait of a lion",        # Image
#     "how to use the tool",                      # Chat
#     "provide details on the tool",              # Chat
#     "give me an overview of the tool",          # Chat
#     "create a fantasy landscape with dragons"   # Image
# ]

# # Function to generate mixed payloads for both chat and image queries
# def generate_dynamic_payloads(chat_base, image_base, variations):
#     payloads = []
#     for query in variations:
#         if "portrait" in query or "landscape" in query or "image" in query:
#             # If it's an image generation query, use TOOL_CHAT_IMG
#             new_payload = image_base.copy()
#         else:
#             # Otherwise, use TOOL_CHAT for chat queries
#             new_payload = chat_base.copy()
#         new_payload["query"] = query
#         payloads.append(new_payload)
#     return payloads

# shuffled_payloads = generate_dynamic_payloads(DevPayload.TOOL_CHAT, DevPayload.TOOL_CHAT_IMG, custom_query_variations)
