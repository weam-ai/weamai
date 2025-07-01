user_prompt = """{user_query}"""


context_prompt = """
Analyze the attached video and return a detailed and structured summary that captures the full context of the content.
The output must include:
1. A complete transcript of all spoken content, segmented with accurate timestamps.
2. Descriptions of all key visuals on screen, including UI elements, cursor movements, text, images, or changes that occur.
3. Any notable non-verbal audio cues (e.g., music, sound effects, pauses) with timestamps.
4. A timeline format that groups spoken words, visuals, and other context together at each timestamp.

Use the following structure for each entry in the timeline:
- timestamp: [HH:MM:SS]
- spoken: [Text spoken at that moment]
- visuals: [What is shown on screen]
- notes: [Optional — other relevant context, such as tone, emphasis, or action]

Ensure nothing important is left out. The goal is to capture everything necessary to fully understand the video without watching it.
"""

system_prompt = "You are a video analysis assistant. Your task is to analyze the video."