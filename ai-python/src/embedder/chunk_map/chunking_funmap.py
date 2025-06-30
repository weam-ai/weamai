from src.embedder.spliter.langchain_spliter import custom_text_splitter
from langchain_text_splitters.base import TextSplitter
from typing import List
from src.logger.default_logger import logger

def chunking_data_preparation(text_data: str, splitter:TextSplitter=custom_text_splitter) -> List[str]:
    """
    Splits the given text data into manageable chunks using a specified text splitting function.

    Parameters:
        text_data (str): The text data to be chunked.
        splitter (Callable[[str], List[str]]): A function that takes a string and returns a list of chunks.
            This function is used to split the text data into manageable pieces.

    Returns:
        List[str]: A list of text chunks resulted from splitting the text_data using the splitter function.

    Raises:
        Exception: If the splitting process fails or does not return a list of strings.
    """
    try:
        # Split the text data using the provided splitter function
        texts_chunks_docs = splitter.split_text(text_data)
        
        # Verify that the splitter function returns a list of strings
        if not isinstance(texts_chunks_docs, List) or not all(isinstance(chunk, str) for chunk in texts_chunks_docs):
            raise TypeError("Splitter function must return a list of strings.")

        return texts_chunks_docs
    except Exception as e:
        logger.error(f"An error occurred during text data preparation: {e}")
        return []

def chunking_datapage_preparation(text_data: List[str], splitter=custom_text_splitter):
    # Split the text data using the provided or default splitter
    # texts_chunks_docs = splitter.split_text(text_data)

    # Ensure the function returns a list of strings
    return text_data


map_functions = {
    'string': chunking_data_preparation,
    'page_wise': chunking_datapage_preparation,
}