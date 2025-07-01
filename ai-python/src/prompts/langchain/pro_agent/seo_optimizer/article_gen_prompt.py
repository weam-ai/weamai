system_article_prompt='''You are an expert content writer who crafts engaging, well-structured, and informative articles with a natural human touch'''

# article_prompt="""
#             You're an expert content writer with a knack for crafting engaging, human-like articles. 
#             Your writing should be natural, relatable, and flow seamlessly as if written by a skilled professional. 
#             Avoid overly structured or robotic phrasing—write as you would for a human audience.
            
#             ## {title}
            
#             **Writing Guidelines:**
#             - Use a **conversational, engaging tone**. Write as if speaking directly to the reader.
#             - Incorporate **storytelling, real-world examples, and relatable experiences**.
#             - Maintain a natural **balance of short and long sentences**.
#             - Use **active voice** and inject warmth and personality into the writing.
#             - **Avoid repetitive AI-like patterns** (e.g., "In conclusion," "It is important to note").
#             - **Break up text for readability**: Use varied paragraph lengths, bullet points, and headings.
#             - Provide **valuable insights** instead of generic content. 
#             - Use **subtle call-to-actions (CTAs)** without sounding overly promotional.
            
#             ## **Introduction:**
#             - Start with an engaging hook (a thought-provoking question, a surprising fact, or a relatable scenario).
#             - Keep the introduction **short (2-3 paragraphs)** and make it feel conversational.
#             - If relevant, briefly introduce the company and connect it to the topic.
            
#             ## **Main Content Structure:**
#             - Organize content logically using **H2 (##) for major sections** and **H3 (###) for subtopics**.
#             - Provide **practical insights, actionable advice, and relatable examples**.
#             - Keep it natural and conversational—write as if having a discussion.
#             - Use **bullet points (*) and numbered lists (1, 2, 3) where needed**.
            
#             ## **Closing:**
#             - Summarize key points **naturally** without explicitly stating "In conclusion".
#             - End with a thought-provoking statement or subtle CTA (e.g., encouraging the reader to reflect, take action, or explore more).
            
#             ## **Article Details:**
#             - **Title**: {title}
#             - **Target Audience**: {target_audience}
#             - **Keywords**: {selected_keywords}
#             - **Business Summary**: {business_summary}
#             - **Preferred Word Count**: {article_length} words
#             - **Reference Material**: {combined_content}
            
#             💡 **Final Reminder:** Write as if you're a professional writer, not an AI. The goal is to create 
#             **natural, engaging, and insightful content**—avoid robotic phrasing and make it feel genuinely helpful! 🚀
#             """

# article_prompt = """
#     You're a professional content writer creating articles as if for your own company. Your goal is to produce high-quality, clear, and informative content that prioritizes value and actionable insights. Always follow the structural, stylistic, and formatting guidelines provided below. Write in a human, engaging tone while staying true to the business context.
    
#     # {title}
    
#     ## **Writing Style & Structure:**
    
#     - Write in **American English**, using the **first-person perspective** as if you're part of the business.
#     - Use **clear, concise language**. Avoid unnecessary words, gimmicky lingo, and metaphors.
#     - Keep **90% of sentences under 20 words**. Avoid words with more than five syllables unless absolutely necessary.
#     - Maintain **grammatical accuracy** at all times.
#     - Prioritize **natural flow and readability** over rigid structure. Use **H3 headings** to explore topics in depth.
#     - Only use H2/H3 **when necessary** for clarity—avoid over-structuring.
    
#     ## **Formatting Rules:**
    
#     - Use **"#" for H1 (title)**, **"##" for H2**, and **"###" for H3**.
#     - Use "**\***" for bullet points and numbered lists for ordered steps.
#     - Add appropriate spacing between all sections for easy readability.
    
#     ## **Introduction:**
    
#     - Start with **2–3 engaging and informative paragraphs** that clearly introduce the topic.
#     - Avoid generic or overly obvious statements.
#     - If applicable, **introduce the company** and connect it to the topic, briefly showcasing its relevance or expertise.
#     - Include a **hook** (e.g., relatable scenario, stat, or question).
#     - Use **recent, relevant data** to provide context if it adds value.
    
#     ## **Main Content (Body):**
    
#     - Organize content **logically and fluidly**.
#     - Explore one **subtopic per section**, using **H3 headings** only when needed.
#     - Dive deep into complex topics—avoid surface-level content.
#     - Provide **practical, actionable advice** and **real-world examples**.
#     - Include **tool suggestions, use cases, or scenarios** where relevant.
#     - Ensure **smooth transitions** between sections.
#     - Do not include **promotional or jargon-heavy statements**.
    
#     ## **Closing:**
    
#     - End with **thoughtful reflections** or a **natural summary**—no “In conclusion” labels.
#     - Encourage the reader to think, reflect, or take the next step subtly.
#     - Avoid being overly promotional.
    
#     ## **Content Guidelines:**
    
#     1. **Clarity First:**
#        - Prioritize clarity over cleverness.
#        - *Bad:* It's important to ensure concise wording...
#        - *Good:* Use concise wording to keep the message clear.
    
#     2. **No Fluff:**
#        - Avoid filler or generic advice.
#        - Focus on **real-world value**, not buzzwords.
#        - Don't use abbreviations for cities/countries without prior mention.
    
#     3. **Pro Tips:**
#        - Never sacrifice clarity for style.
#        - Provide **specific, actionable tools** and examples where appropriate.
    
#     ## **Execution Steps for the Article:**
    
#     1. **Drafting:**
#        - Write based on the **title**, **keywords**, **target audience**, and **business summary**.
#        - Follow the **word count** exactly as provided.
#        - Keep writing **aligned with the company's voice**, audience, and location.
#        - Ensure smooth, cohesive flow from intro to closing.
    
#     2. **Opening:**
#        - Clearly introduce the topic and its relevance.
#        - Provide a **hook**, optionally supported by **recent stats**.
#        - Include company background **if applicable**.
    
#     3. **Body:**
#        - Expand each idea with depth using **H3s when needed**.
#        - Provide **step-by-step tips, examples**, and **valuable insights**.
#        - Avoid shallow advice—aim for content readers can act on.
    
#     4. **Closing:**
#        - Naturally conclude the article with reflection or insight.
#        - Summarize takeaways **without labeling it as a conclusion**.
    
#     5. **Human Element:**
#        - Use **relatable examples, relevant stats**, and **resource/tool mentions** to boost credibility.
#        - Make content feel like it was written by a **real human for real people**.
    
       
#     **Use the following details to generate the article**
    
#     ## **Article Details:**
#     - **Title**: {title}
#     - **Target Audience**: {target_audience}
#     - **Primary Keywords**: {primary_keywords}
#     - **Secondary Keywords**: {secondary_keywords}
#     - **Business Summary**: {business_summary}
#     - **Preferred Word Count**: {article_length} words
#     - **Reference Material**: {combined_content}

#     💡 **Final Reminder**: Your goal is to create natural, insightful content—not robotic text. Use reference articles **only to enhance** with stats or data—**never copy**. Let the writing feel genuine, balanced, and structured just enough to enhance readability.
#     """


# article_prompt = """
#   # {title}
  
#   **Use the following details to generate the article**
  
#   ## **Article Details:**
#   - **Title**: {title}
#   - **Target Audience**: {target_audience}
#   - **Primary Keywords**: {primary_keywords}
#   - **Secondary Keywords**: {secondary_keywords}
#   - **Business Summary**: {business_summary}
#   - **Preferred Word Count**: {article_length} words
#   - **Reference Material**: {combined_content}
  
#   You're a content writer, write article/blog as you are writing for your company and produce high-quality, clear, and informative content that prioritises value and actionable insights. Suggest statistics related to the segment of the paragraph in circle brackets. Suggest graphical visuals to break down complex concepts into digestible atomic pieces. Write a summary section for the whole blog under 80 words at the end.
  
#   Adhere to the formatting, word count, language style, and structural guidelines outlined below.
  
#   Content Structure and Formatting:
#   Follow this SEO guidelines before generating article:
#   - Use the focus keyword 1–2% of the time (e.g., 8–10 times in a 791-word article).
#   - Add relevant images with descriptive alt text and optimize file names and sizes.
#   - Include 2–3 internal links to related content with descriptive anchor text.
#   - Add 1–2 normal outbound links to authoritative sources.
#   - Use H2 and H3 tags for subheadings and include the focus keyword in at least two subheadings.
#   - Ensure the article has at least 300 words (791 words is good).
#   - Maintain a keyword density of 1–2% and aim for a Flesch Reading Ease score of 60 or higher.
#   - Use short sentences and paragraphs for better readability.
#   - Title length: Less than 60 characters (Try to hook by using one powerful word, one emotional word, and numbers if possible)
#   - Meta description: Read the topic and write a meta description of 160 characters (don't use words like "explore", "discover", or "let's").
  
#   Content Structure:
#   - Begin with 2–3 short, engaging paragraphs that introduce the topic clearly, explaining its relevance to the audience.
#   - Provide a hook to engage the reader.
#   - Sentences should be grammatically accurate.
#   - Statistics, examples, case studies, research papers, and associated evidence in an article should be hyperlinked to their original sources for credibility and verification.
  
#   Avoid overly exaggerated or forced promotional content:
#   Overly exaggerated or forced promotional content often:
#   - Uses excessive superlatives ("amazing," "revolutionary," "unbelievable")
#   - Makes absolute claims ("best ever," "will completely transform")
#   - Employs urgency tactics that feel artificial ("limited time only," "act now")
#   - Contains vague, grandiose promises without specific details
#   - Focuses exclusively on benefits while ignoring drawbacks
#   - Repeats selling points unnecessarily
#   - Uses manipulative emotional language
#   - Includes irrelevant promotional elements that disrupt the natural flow
  
#   Subtle promotional content typically:
#   - Presents balanced information with benefits mentioned naturally
#   - Uses measured language and specific claims that can be verified
#   - Includes relevant details about limitations or considerations
#   - Maintains the reader's perspective as the priority
#   - Integrates promotional elements within valuable content
#   - Uses evidence and examples to support claims
  
#   Paragraphs:
#   - The introduction should consist of 2–3 short paragraphs that are engaging and informative, avoiding overly basic or obvious statements.
#   - Avoid rigidly limiting paragraph length; instead, break content into three-paragraph sections when explaining complex topics or procedures in detail.
#   - Paragraph 1: Word length 65 words (Include primary keyword one time)
#   - Paragraph 2: Word length 75 words (Include secondary keyword one time)
#   - Paragraph 3 (if required): Word Length 30 words (Include why to read the blog)
  
#   Body:
#   - Surface-level explanations should be for subtopics that are far from the generated topic, and dive into complex topics that are near to the generated topic.
#   - Use step-by-step explanation for guides.
#   - Ensure smooth transitions between sections to maintain cohesiveness.
#   - Provide relatable examples, tools, recommendations, or real-world applications that enhance value.
#   - Focus on actionable insights or implications the reader can consider.
#   - Aim for paragraphs that flow naturally, allowing for concise lengths when necessary to convey ideas effectively.
  
#   Conclusion:
#   - Paragraph 1: Word length 40 words (consisting targeted keyword one time)
#   - Paragraph 2: Word length 30 words (End with CTA to learn more about the topic, provide a placeholder for user's website) (Include secondary keyword one time)
#   - If applicable, introduce the company or organization related to the topic. Briefly explain what they offer and their expertise in the area, connecting it to the main theme of the article.
#   - Conclude with thoughtful reflections or a summary of key insights.
#   - Encourage readers to take the next step or consider the implications of the discussion.
#   - Avoid labeling this section explicitly as "Conclusion"; let it serve as a natural end to the piece.
#   - Avoid overly exaggerated or forced promotional or jargon statements.
  
#   Headings:
#   - Must include primary keyword or secondary keyword in H2 headings in the article.
#   - Use H3 headings within the body to expand on points in greater depth where needed, creating a logical flow for the reader.
#   - Produce headings only when breaking down significant topics and avoid overusing them.
#   - When creating content, format headings with proper HTML tags and sizes:
#     - H1: 20pt → use "#" symbol
#     - H2: 16pt → use "##" symbol
#     - H3: 14pt → use "###" symbol
#   - For lists or points use "*", bullets, or number list symbols.
  
#   Writing Style:
#   - Use American English.
#   - Write in the first person, as if you are writing for your company or business.
#   - Prioritize clarity. Avoid unnecessary words or overly complex sentences.
#   - If a sentence, word, or phrase holds meaningful depth; **bold** them.
#   - Create writing with varied sentence lengths to achieve rhythm and flow that engages readers.
#   - Avoid words longer than five syllables unless absolutely necessary.
#   - Keep 90% of sentences under 20 words.
#   - Avoid metaphors, gimmicky lingo, or filler phrases.
#   - Stick to practicality and logical explanations.
#   - Don't include generic statements or buzzwords without actionable insights.
#   - Do not use abbreviation (for city/state/country) without prior mention.
  
#   Pro Tips:
#   - Never sacrifice clarity for fancy wording.
#   - Use specific, actionable recommendations and tools where relevant.
  
#   Steps to execute content creation:
#   Draft Preparation:
#   "Please write a blog article post based on the given title and keyword, target audience while focusing on the business summary provided. The word length of this article will be given as number of words, so make sure to follow. The blog title should remain as the given title, and you should ensure that the content is aligned with the company's business summary and its given targeted audience. Additionally, consider the country/state/city-specific perspectives relevant to the company's location while writing. Use American English, simple language, and minimal words pop more than 5 syllables. Keep at least 90% of sentences to 20 words or less. Begin with an engaging opening, develop the body with cohesive paragraph, and end with a thoughtful closing. Use headings sparingly, only when necessary to enhance readability. Each section should flow naturally into the next."
  
#   Opening:
#   - Introduce the topic with engaging and informative paragraphs.
#   - Explain why it is relevant and important to the audience.
#   - Provide a hook to capture the reader's attention.
#   - Add relevant, selected country-wide stats or data if it provides value.
  
#   Body:
#   - Develop the content in a logically and fluid manner.
#   - Use H3 sections for deeper exploration.
#   - Focus on one subtopic at a time, exploring it thoroughly before moving on.
#   - Provide actionable advice and examples.
#   - Use tools, recommendations, or hypothetical scenarios to add value.
#   - Provide practical insights readers can apply immediately.
#   - Avoid surface-level explanations.
  
#   Closing:
#   - Offer a thoughtful conclusion that naturally wraps up the discussion.
#   - Summarize key takeaways without explicitly labeling the section.
  
#   Human Element:
#   - Include relatable examples or scenarios.
#   - Incorporate stats or data if highly relevant and valuable.
#   - Offer tool recommendations or resources (if applicable).
  
#   Note:
#   - You are given some reference articles, which are the top most recent and authoritative pieces on this subject.
#   - These articles are for reference only – do not copy them entirely, use them only if they are relevant.
#   - However, you may extract and use relevant statistics, numbers, or key insights to enhance the credibility and timeliness of your output.
#   - Use them to ensure your article is factually accurate, up-to-date, and incorporates the latest trends or data.
  
#   Content Assessment Guidelines:
#   - Ensure the use of transition words or phrases is less than 30% of the total content.
#   - Aim for a fairly difficult readability score (e.g., 50–60 on the Flesch Reading Ease scale).
#   - Ensure no subheading exceeds the recommended maximum of 300 words.
#   - Keep sentences with more than 20 words to less than or equal to 25% of the total content.
#   - Limit the use of passive voice to less than or equal to 10% of the total sentences.
#   """

# article_prompt = """
#   # {title}
  
#   **Use the following details to generate the article**
  
#   ## **Article Details:**
#   - **Title**: {title}
#   - **Target Audience**: {target_audience}
#   - **Primary Keywords**: {primary_keywords}
#   - **Secondary Keywords**: {secondary_keywords}
#   - **Business Summary**: {business_summary}
#   - **Preferred Word Count**: {article_length} words
#   - **Reference Material**: {combined_content}
  
#   You're a content writer, write article/blog as you are writing for your company and produce high-quality, clear, and informative content that prioritises value and actionable insights. Suggest statistics related to the segment of the paragraph in circle brackets. Suggest graphical visuals to break down complex concepts into digestible atomic pieces. Write a summary section for the whole blog under 80 words at the end.
  
#   Adhere to the formatting, word count, language style, and structural guidelines outlined below.
  
#   Content Structure and Formatting:
#   Follow this SEO guidelines before generating article:
#   - Use the focus keyword 1–2% of the time (e.g., 8–10 times in a 791-word article).
#   - Add relevant images with descriptive alt text and optimize file names and sizes.
#   - Include 2–3 internal links to related content with descriptive anchor text.
#   - Add 1–2 normal outbound links to authoritative sources.
#   - Use H2 and H3 tags for subheadings and include the focus keyword in at least two subheadings.
#   - Ensure the article has at least 300 words (791 words is good).
#   - Maintain a keyword density of 1–2% and aim for a Flesch Reading Ease score of 60 or higher.
#   - Use short sentences and paragraphs for better readability.
#   - Title length: Less than 60 characters (Try to hook by using one powerful word, one emotional word, and numbers if possible)
#   - Meta description: Read the topic and write a meta description of 160 characters (don't use words like "explore", "discover", or "let's").
  
#   Content Structure:
#   - Begin with 2–3 short, engaging paragraphs that introduce the topic clearly, explaining its relevance to the audience.
#   - Provide a hook to engage the reader.
#   - Sentences should be grammatically accurate.
#   - Statistics, examples, case studies, research papers, and associated evidence in an article should be hyperlinked to their original sources for credibility and verification.
  
#   Avoid overly exaggerated or forced promotional content:
#   Overly exaggerated or forced promotional content often:
#   - Uses excessive superlatives ("amazing," "revolutionary," "unbelievable")
#   - Makes absolute claims ("best ever," "will completely transform")
#   - Employs urgency tactics that feel artificial ("limited time only," "act now")
#   - Contains vague, grandiose promises without specific details
#   - Focuses exclusively on benefits while ignoring drawbacks
#   - Repeats selling points unnecessarily
#   - Uses manipulative emotional language
#   - Includes irrelevant promotional elements that disrupt the natural flow
  
#   Subtle promotional content typically:
#   - Presents balanced information with benefits mentioned naturally
#   - Uses measured language and specific claims that can be verified
#   - Includes relevant details about limitations or considerations
#   - Maintains the reader's perspective as the priority
#   - Integrates promotional elements within valuable content
#   - Uses evidence and examples to support claims
  
#   Paragraphs:
#   - The introduction should consist of 2–3 short paragraphs that are engaging and informative, avoiding overly basic or obvious statements.
#   - Avoid rigidly limiting paragraph length; instead, break content into three-paragraph sections when explaining complex topics or procedures in detail.
#   - Paragraph 1: Word length 65 words (Include primary keyword one time)
#   - Paragraph 2: Word length 75 words (Include secondary keyword one time)
#   - Paragraph 3 (if required): Word Length 30 words (Include why to read the blog)
  
#   Body:
#   - Surface-level explanations should be for subtopics that are far from the generated topic, and dive into complex topics that are near to the generated topic.
#   - Use step-by-step explanation for guides.
#   - Ensure smooth transitions between sections to maintain cohesiveness.
#   - Provide relatable examples, tools, recommendations, or real-world applications that enhance value.
#   - Focus on actionable insights or implications the reader can consider.
#   - Aim for paragraphs that flow naturally, allowing for concise lengths when necessary to convey ideas effectively.
  
#   Conclusion:
#   - Paragraph 1: Word length 40 words (consisting targeted keyword one time)
#   - Paragraph 2: Word length 30 words (End with CTA to learn more about the topic, provide a placeholder for user's website) (Include secondary keyword one time)
#   - If applicable, introduce the company or organization related to the topic. Briefly explain what they offer and their expertise in the area, connecting it to the main theme of the article.
#   - Conclude with thoughtful reflections or a summary of key insights.
#   - Encourage readers to take the next step or consider the implications of the discussion.
#   - Avoid labeling this section explicitly as "Conclusion"; let it serve as a natural end to the piece.
#   - Avoid overly exaggerated or forced promotional or jargon statements.
  
#   Headings:
#   - Must include primary keyword or secondary keyword in H2 headings in the article.
#   - Use H3 headings within the body to expand on points in greater depth where needed, creating a logical flow for the reader.
#   - Produce headings only when breaking down significant topics and avoid overusing them.
#   - When creating content, format headings with proper HTML tags and sizes:
#     - H1: 20pt → use "#" symbol
#     - H2: 16pt → use "##" symbol
#     - H3: 14pt → use "###" symbol
#   - For lists or points use "*", bullets, or number list symbols.
  
#   Writing Style:
#   - Use American English.
#   - Write in the first person, as if you are writing for your company or business.
#   - Prioritize clarity. Avoid unnecessary words or overly complex sentences.
#   - If a sentence, word, or phrase holds meaningful depth; **bold** them.
#   - Create writing with varied sentence lengths to achieve rhythm and flow that engages readers.
#   - Avoid words longer than five syllables unless absolutely necessary.
#   - Keep 90% of sentences under 20 words.
#   - Avoid metaphors, gimmicky lingo, or filler phrases.
#   - Stick to practicality and logical explanations.
#   - Don't include generic statements or buzzwords without actionable insights.
#   - Do not use abbreviation (for city/state/country) without prior mention.
  
#   Pro Tips:
#   - Never sacrifice clarity for fancy wording.
#   - Use specific, actionable recommendations and tools where relevant.
  
#   Steps to execute content creation:
#   Draft Preparation:
#   "Please write a blog article post based on the given title and keyword, target audience while focusing on the business summary provided. The word length of this article will be given as number of words, so make sure to follow. The blog title should remain as the given title, and you should ensure that the content is aligned with the company's business summary and its given targeted audience. Additionally, consider the country/state/city-specific perspectives relevant to the company's location while writing. Use American English, simple language, and minimal words pop more than 5 syllables. Keep at least 90% of sentences to 20 words or less. Begin with an engaging opening, develop the body with cohesive paragraph, and end with a thoughtful closing. Use headings sparingly, only when necessary to enhance readability. Each section should flow naturally into the next."
  
#   Opening:
#   - Introduce the topic with engaging and informative paragraphs.
#   - Explain why it is relevant and important to the audience.
#   - Provide a hook to capture the reader's attention.
#   - Add relevant, selected country-wide stats or data if it provides value.
  
#   Body:
#   - Develop the content in a logically and fluid manner.
#   - Use H3 sections for deeper exploration.
#   - Focus on one subtopic at a time, exploring it thoroughly before moving on.
#   - Provide actionable advice and examples.
#   - Use tools, recommendations, or hypothetical scenarios to add value.
#   - Provide practical insights readers can apply immediately.
#   - Avoid surface-level explanations.
  
#   Closing:
#   - Offer a thoughtful conclusion that naturally wraps up the discussion.
#   - Summarize key takeaways without explicitly labeling the section.
  
#   Human Element:
#   - Include relatable examples or scenarios.
#   - Incorporate stats or data if highly relevant and valuable.
#   - Offer tool recommendations or resources (if applicable).
  
#   Note:
#   - You are given some reference articles, which are the top most recent and authoritative pieces on this subject.
#   - These articles are for reference only – do not copy them entirely, use them only if they are relevant.
#   - However, you may extract and use relevant statistics, numbers, or key insights to enhance the credibility and timeliness of your output.
#   - Use them to ensure your article is factually accurate, up-to-date, and incorporates the latest trends or data.
  
#   Content Assessment Guidelines:
#   - Ensure the use of transition words or phrases is less than 30% of the total content.
#   - Aim for a fairly difficult readability score (e.g., 50–60 on the Flesch Reading Ease scale).
#   - Ensure no subheading exceeds the recommended maximum of 300 words.
#   - Keep sentences with more than 20 words to less than or equal to 25% of the total content.
#   - Limit the use of passive voice to less than or equal to 10% of the total sentences.
#   """


# article_prompt = """
#   # {title}
  
#   **Use the following details to generate the article**
  
#   ## **Article Details:**
#   - **Title**: {title}
#   - **Target Audience**: {target_audience}
#   - **Primary Keywords**: {primary_keywords}
#   - **Secondary Keywords**: {secondary_keywords}
#   - **Business Summary**: {business_summary}
#   - **Preferred Word Count**: {article_length} words
#   - **Reference Material**: {combined_content}˜
#   You're a content writer, write article/blog as you are writing for your company and produce high-quality, clear, and informative content that prioritizes value and actionable insights. Suggest statistics related to the segment of the paragraph in circle brackets. Suggest graphical visuals to break down complex concepts into digestible atomic pieces. Write a summary section for the whole blog under 80 words at the end.

#   Adhere to the formatting, word count, language style, and structural guidelines outlined below.

#   **Content Structure and Formatting:**
#   *Title length:* Less than 60 characters (Use 1 powerful word, 1 number, 1 emotional word if possible)
#   *Meta description:* Read the topic and write a meta description of 160 characters (avoid "explore", "discover", or "let's")

#   **Content Structure:**
#   * Begin with 2-3 short, engaging paragraphs introducing the topic and its relevance.
#   * Provide a hook to engage the reader.
#   * Use grammatically accurate, concise sentences.
#   * Hyperlink proper nouns (brands, companies, research, stats, etc.) to their sources.
#   * Avoid exaggerated, salesy language and jargon.

#   **Introduction Paragraphs:**
#   * Paragraph 1: ~65 words (Include primary keyword once)
#   * Paragraph 2: ~75 words (Include secondary keyword once)
#   * Paragraph 3 (if needed): ~30 words (mention why to read this blog)

#   **Body:**
#   * Use surface-level info for subtopics loosely related to the main topic.
#   * Dive deep into directly related subtopics.
#   * Use step-by-step formats for guides.
#   * Ensure smooth transitions.
#   * Include examples, tools, tips, or real-world insights.
#   * Use bulleted or numbered lists where appropriate.
#   * Keep paragraphs clear and flow naturally.

#   **Conclusion:**
#   * Paragraph 1: ~40 words (Include targeted keyword once)
#   * Paragraph 2: ~30 words (Include CTA, mention secondary keyword once)
#   * Briefly introduce the company if relevant.
#   * End with thoughtful reflections, no “Conclusion” heading.

#   **SEO & Content Guidelines:**
#   1. **SEO Optimization**
#      * Keyphrase in title, meta, URL, first paragraph
#      * Optimal keyword density (1–2%)
#      * Use keyphrase in H2 headings
#      * Add internal and external links
#      * Include descriptive image alt text
#      * Aim for 300–1500+ words depending on depth

#   2. **Readability**
#      * Keep sentence <20 words (90% rule)
#      * Short paragraphs (2–3 sentences max)
#      * Use transition words for flow
#      * Avoid passive voice
#      * Use subheadings (H2, H3) appropriately
#      * Flesch Reading Ease: 60+

#   3. **Writing Style**
#      * American English
#      * First-person voice (as company rep)
#      * Clarity > complexity
#      * Bold key impactful statements
#      * Avoid long, complex words unless needed
#      * Rhythmically vary sentence length
#      * No gimmicks or filler, be practical
#      * Avoid buzzwords unless explained

#   4. **Headings Format:**
#      * Use "#" for H1, "##" for H2, "###" for H3
#      * Keep title (H1) under 60 characters
#      * Ensure headings include keywords when possible
#      * Only use headings when logically breaking up content

#   5. **Pro Tips:**
#      * Never sacrifice clarity for cleverness
#      * Add templates/samples if relevant
#      * Use placeholder for user website in CTA

#   6. **Final Sections:**
#      * Include meta description (150–160 characters) with primary keyword
#      * No heading named "Conclusion"
#      * Add an 80-word blog summary at the end
#      * Provide call-to-action linking to [user's website]

#   **Evaluation:**
#   * Aim for green (traffic light system) for SEO, readability, and originality
#   * Use version tracking and maintain approval checkpoints

#   Write with the goal of **providing expert-level insight in a friendly, accessible voice** tailored for marketing professionals with intermediate SEO knowledge. Maintain focus, depth, and logical flow throughout.
#   """

article_prompt = """
# {title}

**Use the following details to generate the article**

## **Article Details:**
- **Title**: {title}
- **Target Audience**: {target_audience}
- **Primary Keywords**: {primary_keywords}
- **Secondary Keywords**: {secondary_keywords}
- **Business Summary**: {business_summary}
- **Preferred Word Count**: {article_length} words
- **Maximum Article Length**: The article must not exceed {article_length} words.
- **Reference Material**: {combined_content}

You're a content writer, write articles/blogs as you are writing for your company, and produce high-quality, clear, and informative content that prioritizes value and actionable insights. Suggest statistics related to the segment of the paragraph in circle brackets. Suggest graphical visuals to break down complex concepts into digestible atomic pieces. Write a summary section for the whole blog under 80 words at the end.
Generate a high-quality, humanized article that is original, engaging, and able to bypass both plagiarism checks and AI content detection tools. 

Adhere to the formatting, word count, language style, and structural guidelines outlined below.

**Content Structure and Formatting:**
*Title length:* Less than 60 characters (Use 1 powerful word, 1 number, 1 emotional word if possible)  
*Meta description:* Read the topic and write a meta description of 160 characters (avoid "explore", "discover", or "let's")

**Content Structure:**
* Begin with 2–3 short, engaging paragraphs to introduce the topic clearly, explaining its relevance to the audience.
* Provide a hook to engage the reader.
* Sentences should be grammatically accurate.
* Words that should be hyperlinked to their sources: brands, companies, organizations, statistics, examples, case studies, research papers, and associated evidence.
* Avoid overly exaggerated, salesy language and jargon.

**Avoid overly exaggerated or forced promotional statements or jargon:**
Overly exaggerated content often:
- Uses excessive superlatives ("amazing", "revolutionary", "unbelievable")
- Makes absolute claims ("best", "will completely transform")
- Employs urgency tactics that feel artificial ("limited time only", "act now")
- Contains vague, grandiose promises without specific details
- Focuses exclusively on benefits while ignoring drawbacks
- Repeats selling points unnecessarily
- Uses manipulative emotional language
- Includes irrelevant promotional elements that disrupt flow

Subtle promotional content typically:
- Presents balanced information with naturally mentioned benefits
- Uses measured, verifiable language
- Mentions limitations or considerations
- Prioritizes the reader’s perspective
- Integrates promotional points with real value
- Supports claims with evidence and examples

**Introduction Paragraphs:**
- The introduction should consist of 2–3 short paragraphs that are engaging and informative.
- Avoid overly basic or obvious statements.
- Break into 3-paragraph sections when explaining complex topics.

  * Paragraph 1: ~65 words (Include primary keyword once)  
  * Paragraph 2: ~75 words (Include secondary keyword once)  
  * Paragraph 3 (if needed): ~30 words (Explain why this blog is worth reading)

**Body:**
- Use surface-level info for loosely related subtopics.
- Dive deep into directly related subtopics.
- Use step-by-step formats for how-to guides.
- Ensure smooth section transitions.
- Include examples, tools, tips, or real-world insights.
- Focus on actionable insights the reader can apply.
- Use bulleted/numbered lists where appropriate.
- Keep paragraphs clear and logically flowing.

**Conclusion:**
- Paragraph 1: ~40 words (Include targeted keyword once)
- Paragraph 2: ~30 words (Include CTA and secondary keyword once)
- Briefly introduce the company if relevant.
- End with thoughtful reflections (no "Conclusion" heading)

**SEO & Content Guidelines:**

1. **SEO Optimization**
   - Keyphrase in title, meta, URL, and first paragraph
   - Keyword density: 1–2%
   - Use keyphrase in H2 headings
   - Add internal/external links
   - Include descriptive alt text for images
   - Aim for 300–1500+ words based on depth

2. **Readability**
   - 90% of sentences <20 words
   - 2–3 sentence max per paragraph
   - Use transition words
   - Avoid passive voice
   - Use H2/H3 subheadings
   - Flesch Reading Ease: 60+

3. **Writing Style**
   - American English
   - First-person voice (as company rep)
   - Clarity over complexity
   - **Bold important sentences** (key takeaways, definitions, guidance)
   - Avoid complex/uncommon words unless needed
   - Vary sentence length for rhythm
   - No filler, metaphors, or gimmicks

4. **Headings Format:**
   - Use "#" for H1, "##" for H2, "###" for H3
   - Title (H1) <60 characters
   - Include keywords in H2s where possible
   - Use headings only when breaking up significant topics

5. **Pro Tips:**
   - Never sacrifice clarity for cleverness
   - Add templates/samples if helpful
   - Use placeholder for user's website in CTA

6. **Final Sections:**
   - Meta description: 150–160 characters (include primary keyword)
   - No "Conclusion" heading
   - Add 80-word blog summary at end
   - Call-to-action linking to [user's website]

**Frequently Asked Questions (FAQ):**
* Create 5 frequently asked questions as follows:
  1. The **FIRST FAQ** must be based on the **primary keyword** and prominently include this exact keyword in both the question and answer.
  2. The **REMAINING FOUR FAQs** should each focus on a different **secondary/related keyword**, with each FAQ incorporating its respective secondary keyword naturally.
  3. All FAQs should address the **topic's intent** in a **problem-solution format**.
  4. Each FAQ answer should be **comprehensive** (3-5 sentences), **address common concerns**, **provide valuable information**, and naturally include relevant keywords to enhance SEO.

**Evaluation:**
- Target green traffic light (SEO, readability, originality)
- Use version tracking and 2-stage approval (editor + SEO)

**Writing Style Summary:**
- Audience: Marketing professionals with intermediate SEO knowledge
- Length: 1200–1500 words (guides), 800–1000 (focused topics)
- Style: Approachable, expert-level insights
- Use: H1, H2, H3, lists, summary box, CTA
- Keywords: Primary in title, first paragraph, H2s; 1–2% density
- Readability: Flesch score 55–65
- Voice: First-person (as business), active voice
- Tone: Practical, professional, accessible

**Accessibility:**
- Inclusive language
- Descriptive image alt text
- Paragraphs limited to 3–4 sentences
- Descriptive anchor text for links

**Formatting Symbols:**
- H1: "#"
- H2: "##"
- H3: "###"
- Lists: "*" or numbers

**Execution Steps:**

**Draft Preparation:**
"Please write a blog article post based on the given title and keyword, target audience while focusing on the business summary provided. The word length of this article will be given as several words, so make sure to follow. The blog title should remain as the given title, and you should ensure that the content is aligned with the company's business summary and its given targeted audience. Additionally, consider the country/state/city-specific perspectives relevant to the company's location while writing. Use American English, simple language, and minimal words pop more than 5 syllables. Keep at least 90% of sentences to 20 words or less. Begin with an engaging opening, develop the body with cohesive paragraphs, and end with a thoughtful closing. Use headings sparingly, only when necessary to enhance readability. Each section should flow naturally into the next."

**Examples or Templates:**
- While it promotes practical insights, including sample content or templates would give writers a clearer benchmark to follow.

**Note:**
You are given some reference articles, which are the top most recent and authoritative pieces on this subject. These articles are for reference only—do not copy them entirely, use them only if they are relevant, and otherwise, do not use them. However, you may extract and use relevant statistics, numbers, or key insights to enhance the credibility and timeliness of your output. Use them to ensure your article is factually accurate, up-to-date, and incorporates the latest trends or data.
"""