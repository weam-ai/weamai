class HfCanvasToolDescription:
    REGEX_REPLACE_TOOL_DESCRIPTION="""
        Function to replace a substring in the original string based on the provided regular expression pattern.
        
        Strictly,This function is designed to be invoked only once per execution to ensure efficiency and clarity in its operation.
        The Parameters Names below should not be changed
        Parameters:
        - regex_pattern (str): The regex pattern that identifies the substring(s) to replace.
        - replacement_string (str): The string that will replace the matched substring(s).The Replacement String should be revised on the basis of selected_text
        - selected_text(str):This is String which is to be replaced By replacement_string.It's the Reference For Replacement String.
        Returns:
        - str: The updated string after replacements. Only the first occurrence of the pattern will be replaced.
        """

class HfToolDescription:
    SIMPLE_CHAT_V2="""
        A versatile conversation tool designed to generate responses for various user inputs, including code, text-related queries, and image descriptions.
        When to use this tool:
        Responding to general questions.
        Handling code or text-related queries.
        Providing descriptions for images based on user requests.
        """
    HUGGINGFACE_IMAGE_GEN="""An image generation and modification tool that enables users to create images from text descriptions and make various visual changes to the generated images. Users can remove objects, replace elements, insert new items,Edit Images and make other detailed modifications to the images directly using the tool."""