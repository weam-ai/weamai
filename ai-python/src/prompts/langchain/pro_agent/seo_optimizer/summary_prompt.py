system_prompt = """You are an expert business strategist."""
summary_prompt = """
    Analyze the company's details to create a structured and professional business summary. 
    If any information is missing, intelligently infer it using industry knowledge, but clearly indicate inferred details.
    Generate a comprehensive and strictly factual summary based on the following details:

    ### **Company Overview:**
    - **Company Name:** {project_name} (Mandatory, do not proceed if missing)
    - **Headquarters:** {location} (Mandatory, do not proceed if missing)
    - **Website:** {website_url} (Mandatory, do not proceed if missing)
    - **Website Content:** {website_content} (Mandatory, do not proceed if missing)
    - **Founding Year & Industry:** Determine or infer the founding year and industry category, but explicitly state if inferred.

    ### **Business Details:**
    - **Mission & Core Values:** Derive or generate a likely mission statement and core values, but clearly indicate if inferred.
    - **Products & Services:** Identify and describe the key offerings based on provided details only.

    ### **Market Position & Competitive Landscape:**
    - **Target Audience:** Define the company’s primary customer segments based on provided data only.
    - **Competitive Positioning:** Evaluate its market standing and unique value proposition, but avoid assumptions.
    - **Competitors:** Identify potential competitors within the industry based on factual data.

    ### **Recent Developments:**
    - **News & Updates:** Highlight recent announcements such as product launches, partnerships, or investments based on provided data only.
    - If no updates are available, explicitly state "No recent developments provided."

    ### **Final Summary:**
    - Provide a concise conclusion summarizing the company's key aspects, industry impact, and market relevance.
    - Ensure the summary is strictly factual, well-structured, engaging, and easy to understand.
    - The response must be complete and should not cut off mid-sentence.
    - Aim for a response length of approximately 500-700 words for thorough coverage.

    Strictly,Return the final response strictly as a plain string with a clear list of points. Do not use markdown, formatting symbols, line breaks. Ensure the response is presented as a single continuous text block.
    """


audience_prompt = """
    Identify and list the primary target audience segments for the following details:
    
    - **Company Name:** {project_name}
    - **Industry:** {industry}
    - **Target Location:** {location}
    - **Target Keywords:** {target_keywords}
    
    Ensure the response is concise and provides only the names of the audience segments seperated  by comma.
    The list should be clear, relevant, and easy to understand.
    Return the final response as a plain string without additional explanations or markdown formatting, ensuring the list contains no more than 15 target audience segments.
    """
