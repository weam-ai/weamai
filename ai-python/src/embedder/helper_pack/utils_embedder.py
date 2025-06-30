import uuid
import tiktoken
import os
from dotenv import load_dotenv
from src.logger.default_logger import logger

load_dotenv()


def get_default_key(api_key_id:str=None):
    if api_key_id=="1":
        api_key=os.environ.get("OPENAI_API_KEY")
        return api_key
    
def get_default_key_url(api_url_id:str=None):
    if api_url_id=="1":
        api_url=os.environ.get("RAY_SERVE_EMBEDDING_URL")
        return api_url


def addition_metadata(texts_chunks_docs, tag="current_affair_feb_2024_v_2.pdf"):
    """
    Augments a list of text documents with metadata, including a unique identifier and a tag.

    Parameters:
        texts_chunks_docs (list of str): The text documents to be processed.
        tag (str, optional): A tag to associate with each document for categorization.

    Returns:
        list of dict: A list of dictionaries, each representing a processed document with metadata.

    Raises:
        Exception: If the operation cannot be completed due to an error.
    """
    try:
        documents = []
        for index, text in enumerate(texts_chunks_docs):
            unique_id = uuid.uuid4().hex
            documents.append({
                "id": unique_id,
                "values": None,
                "metadata": {"tag": tag, "text": text, "index": index, "unique_id": unique_id}
            })
        return [{"node": node} for node in documents]
    except Exception as e:
        logger.error(f"An error occurred during metadata addition: {e}", exc_info=True)
        return []




def addition_metadata_openai(texts_chunks_docs, tag="current_affair_feb_2024_v_2.pdf", **kwargs):
    """
    Augments a list of text documents with metadata, including a unique identifier and a tag.
    Additional metadata can be added via keyword arguments.

    Parameters:
        texts_chunks_docs (list of str): The text documents to be processed.
        tag (str, optional): A tag to associate with each document for categorization.
        **kwargs: Additional keyword arguments to include as metadata.

    Returns:
        list of dict: A list of dictionaries, each representing a processed document with metadata.

    Raises:
        Exception: If the operation cannot be completed due to an error.
    """
    try:
        documents = []
        file_name=kwargs.get("file_name")
        for index, text in enumerate(texts_chunks_docs):
            unique_id = uuid.uuid4().hex
       
            # Create a metadata dictionary that includes the default and any additional kwargs.
            metadata = {"tag": tag, "text": f"{file_name}:"+f"chunk:{index}:"+text, "index": index, "unique_id": unique_id}
            metadata.update({"db_file_id":kwargs.get("id")})  # Merge additional kwargs into the metadata.
            combined_id = f'{tag}#{unique_id}'
            documents.append({
                "id": combined_id,
                "values": None,  # Preserved as None or can be adjusted if needed.
                "metadata": metadata
            })
        return documents
    except Exception as e:
        logger.error(f"An error occurred during metadata addition: {e}", exc_info=True)
        return []
    


def addition_metadata_qdrant(texts_chunks_docs, tag="current_affair_feb_2024_v_2.pdf", **kwargs):
    """
    Prepares documents in the structure expected by Qdrant, augmenting with metadata.

    Parameters:
        texts_chunks_docs (list of str): The text documents to be processed.
        tag (str, optional): A tag to associate with each document for categorization.
        **kwargs: Additional keyword arguments to include as metadata.

    Returns:
        list of dict: A list of dictionaries, each representing a processed document with metadata for Qdrant.

    Raises:
        Exception: If the operation cannot be completed due to an error.
    """
    try:

        documents = []
        file_name = kwargs.get("file_name")
        db_file_id = kwargs.get("id")
        brain_id = kwargs.get("brain_id", None)
        for index, text in enumerate(texts_chunks_docs):
            unique_id = uuid.uuid4().hex
            payload = {
                "tag": tag,
                "text": f"{file_name}:chunk:{index}:{text}",
                "index": index,
                "unique_id": unique_id,
                "db_file_id": db_file_id,
                "brain_id": brain_id
            }
            documents.append({
                "id": unique_id,
                "payload": payload,
                "vector": None  # Placeholder for embedding vector
            })
        return documents
    except Exception as e:
        logger.error(f"An error occurred during Qdrant metadata addition: {e}", exc_info=True)
        return []

metadata_map={
    "addition_metadata":addition_metadata,
    "addition_metadata_openai":addition_metadata_openai,
    "addition_metadata_rayserve": addition_metadata_openai,
    "addition_metadata_qdrant":addition_metadata_qdrant
}


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def batch_strings(strings: list, encoding_name: str, max_tokens_per_batch: int = 900000) -> list:
    """
    Batches a list of strings based on the number of tokens, using a specified encoding model.

    Parameters:
        strings (list of str): The strings to be batched.
        encoding_name (str): The name of the encoding model used to tokenize the strings.
        max_tokens_per_batch (int, optional): The maximum number of tokens allowed per batch.

    Returns:
        list of list of str: A list of string batches, each batch containing strings that together do not exceed the token limit.

    Raises:
        Exception: If the operation cannot be completed due to an error.
    """
    try:
        batches = []
        current_batch = []
        current_batch_token_count = 0
        encoding = tiktoken.encoding_for_model(encoding_name)  # Initialize the encoding once

        for string in strings:
            string_token_count = len(encoding.encode(string))

            if current_batch_token_count + string_token_count > max_tokens_per_batch:
                if current_batch:  # Only add non-empty batches
                    batches.append(current_batch)
                current_batch = [string]
                current_batch_token_count = string_token_count
            else:
                current_batch.append(string)
                current_batch_token_count += string_token_count

        if current_batch:
            batches.append(current_batch)

        return batches
    except Exception as e:
        logger.error(f"An error occurred during string batching: {e}", exc_info=True)
        return []
