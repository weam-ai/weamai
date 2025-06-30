import re

async def replace_citations(text, urls):
    def replacement(match):
        # Extract citation indices from the match
        indices = match.group(0)[1:-1].split('][')
        # Format them as links using the URLs provided
        formatted_links = ', '.join(f"[{i}]({urls[int(i) - 1]})" for i in indices if int(i) - 1 < len(urls))
        return formatted_links

    # Regex pattern to find citations like [3][4], [3], etc.
    citation_pattern = r'\[(\d+)\](?:\[(\d+)\])*(?=[.\n]|$)'

    # Regex pattern to match code blocks
    code_block_pattern = r'```'
   
        # Split the text into code and non-code sections
    sections = re.split(f'({code_block_pattern}.*?{code_block_pattern})', text, flags=re.S)

    # Process only non-code sections
    for i in range(len(sections)):
        # Check if the section is not a code block
        if not (sections[i].startswith('```') and sections[i].endswith('```')):
            sections[i] = re.sub(citation_pattern, replacement, sections[i])

    # Combine the sections back into a single string
    processed_msg = ''.join(sections)

    # Additional processing for citations with hyperlinks
    citation_with_link_pattern = r'\[(\d+)\]\(([^)]+)\)'
    processed_msg = re.sub(citation_with_link_pattern, lambda match: f" [{match.group(1)}]({match.group(2)})", processed_msg)
    # processed_msg=format_response_with_sources(processed_msg, urls)
    return processed_msg


def format_response_with_sources(response: str, citations: list) -> str:
    """
    Appends a formatted list of sources to the given response.

    Args:
        response (str): The main response text.
        citations (list): A list of citation URLs to include as sources.

    Returns:
        str: The formatted response with sources appended.
    """
    if citations:
        formatted_sources = "\n".join([f"- {citation}" for citation in citations])
        response += f"\n\nSources:\n{formatted_sources}"
    return response