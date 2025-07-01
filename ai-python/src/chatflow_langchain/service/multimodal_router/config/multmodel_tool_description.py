class ToolDescription:
    WEB_ANALYSIS='''
    Deeply analyze multiple or single webpages or URLs provided by the user.
    
    Functionality:
    - Fetch and parse page content: text, images, metadata.
    - Generate structured summaries.
    - Highlight important sections.
    - Extract entities, identify sentiment, themes, and key statistics.

    Parameters:
    - original_query (str): The current user's input query. **Do not modify** this parameter.
    - implicit_reference_urls (List[str]): A list of URLs that are implicitly referenced in the user's query.

    Runtime Behavior:
    - STRICTLY: Only the `implicit_reference_urls` parameter should be passed to the tool at runtime.
      This list must include all URLs implicitly referenced by the user's query.
    - Do not invoke this tool more than once per user query — all relevant URLs must be included in a **single call**.
    - Use `implicit_reference_urls` only when the user query **does not explicitly contain a URL**, 
      but instead refers to previously mentioned or related pages.
    '''
    IMAGE_GENERATE="""An image generation and modification tool that enables users to create images from text descriptions and make various visual changes to the generated images. Users can remove objects, replace elements, insert new items,Edit Images and make other detailed modifications to the images directly using the tool.Tool supports a variety of image sizes and aspect ratios, including 1024x1024 for Square images,1024x1792 for Portrait images and 1792x1024 for Landscape images
    1024×1024 (Square): Ideal for social media posts, profile pictures, digital artwork, and product images.
    1024×1792 (Portrait): Perfect for mobile content, social media stories, and vertical ads.
    1792×1024 (Landscape): Great for presentations, video thumbnails, website banners, and widescreen displays.
    """
    SIMPLE_CHAT="""A versatile conversation tool designed to generate responses for various user inputs, including code, text-related queries, and image descriptions.
        When to use this tool:

        Responding to general questions.
        Handling code or text-related queries.
        Providing descriptions for images based on user requests.

    """
    CUSTOMGPT_WEB_ANALYSIS_TOOL='''
        Website Analysis Tool

        Purpose:
        This tool is optimized to fetch and deeply analyze one or more web pages or URLs provided directly by the user. It parses webpage content including text, images, metadata, and embedded elements, and returns structured insights.

        Capabilities:
        - Summarize full articles or web stories from news/media/blogs.
        - Extract key themes, entities (people, places, organizations), quotes, images, and statistics.
        - Detect sentiment, tone, and user intent behind the content.
        - Segment and highlight important sections like announcements, statements, stats, etc.
        - Return structured JSON summaries or clean markdown when needed.

        Use this tool for:
        - Analyzing articles, press releases, blog posts, or any informational webpage.
        - Generating human-readable or structured summaries from links.
        - Responding to queries like "Summarize this article", "What does this news story say", "What are the key points in this blog", etc.

        Input: One or more URLs provided directly by the user.
        Note: Do not choose this tool if the user is simply asking a general knowledge question without a link.
        '''

    RAG_CONVERSATION="""A dynamic conversational tool that generates responses by integrating information retrieval and generative capabilities. It is optimized for responding to a wide range of user inputs, including code, general knowledge queries, and image descriptions.

        When to use this tool:

        Answering factual or information-based questions.
        Assisting with coding tasks, debugging, or generating code snippets.
        Providing descriptive responses for user-provided image prompts or generating new visuals based on detailed requests."""