class ToolDescritpion:
    WEB_ANALYSIS='''
    Deeply analyze multiple or single webpages or URLs provided by the  user.
    Fetch and parse page content text, images, metadata. Generate structured summaries
    highlight sections, extract entities, identify sentiment, themes, key stats, etc.
    original_query: str is current user inputs query don't modify this parameter.
    STRICTLY: Only the `implicit_reference_urls` parameter should be passed to the tool at runtime. This list must include all URLs implicitly referenced by the user's query. Do not invoke this tool more than once per user query—all relevant URLs must be included in a single call.
    This parameter is used only when the user query  does not explicitly contain a URL, but contains language that refers to previously mentioned or related pages.
    '''
    IMAGE_GENERATION="""An image generation and modification tool that enables users to create images from text descriptions and make various visual changes to the generated images. Users can remove objects, replace elements, insert new items,Edit Images and make other detailed modifications to the images directly using the tool.Tool supports a variety of image sizes and aspect ratios, including 1024x1024 for Square images,1024x1536 for Portrait images and 1536x1024 for Landscape images
    1024x1024 (Square): Ideal for social media posts, profile pictures, digital artwork, and product images.
    1024x1536 (Portrait): Perfect for mobile content, social media stories, and vertical ads.
    1536x1024 (Landscape): Great for presentations, video thumbnails, website banners, and widescreen displays.
    editHistory_flag:bool = False (True,If user Requests to edit or remove objects, replace elements, insert new items,Edit Images and make other detailed modifications from the history) Always pass this flag 
    """
    SIMPLE_CHAT="""A versatile conversation tool designed to generate responses for various user inputs, including code, text-related queries, and image descriptions.
        When to use this tool:

        Responding to general questions.
        Handling code or text-related queries.
        Providing descriptions for images based on user requests.

    """
    WEB_SEARCH_PREVIEW=""" This tool performs a contextual web search or generates a content preview based on user input for real time data,latest news, latest update on internet.thing,
            incorporating conversation history, model configuration, and optional image analysis. It is 
            designed to enhance responses with relevant external information."""
    RAG_CONVERSATION="""A dynamic conversational tool that generates responses by integrating information retrieval and generative capabilities. It is optimized for responding to a wide range of user inputs, including code, general knowledge queries, and image descriptions.

        When to use this tool:

        Answering factual or information-based questions.
        Assisting with coding tasks, debugging, or generating code snippets.
        Providing descriptive responses for user-provided image prompts or generating new visuals based on detailed requests."""