from abc import ABC, abstractmethod

class AbstractCustomGPTRepository(ABC):
    """
    Abstract base class for a Custom GPT Repository. This class defines the
    interface for initializing and retrieving various configuration details
    related to a custom GPT instance.
    """

    @abstractmethod
    def initialization(self, custom_gpt_id: str, collection_name: str):
        """
        Initialize the custom GPT instance with the given ID and collection name.
        
        Args:
            custom_gpt_id (str): Unique identifier for the custom GPT instance.
            collection_name (str): Name of the collection associated with the GPT instance.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Retrieve the name of the custom GPT instance.
        
        Returns:
            str: The name of the GPT instance.
        """
        pass

    @abstractmethod
    def get_gpt_system_prompt(self) -> str:
        """
        Retrieve the system prompt for the custom GPT instance.
        
        Returns:
            str: The system prompt.
        """
        pass

    @abstractmethod
    def get_gpt_goals(self) -> list:
        """
        Retrieve the goals set for the custom GPT instance.
        
        Returns:
            list: A list of goals.
        """
        pass

    @abstractmethod
    def get_gpt_instructions(self) -> list:
        """
        Retrieve the instructions provided to the custom GPT instance.
        
        Returns:
            list: A list of instructions.
        """
        pass

    @abstractmethod
    def get_gpt_llm_key_id(self) -> str:
        """
        Retrieve the large language model (LLM) key ID associated with the custom GPT instance.
        
        Returns:
            str: The LLM key ID.
        """
        pass

    @abstractmethod
    def get_gpt_file_tag(self) -> str:
        """
        Retrieve the file tag used for the custom GPT instance.
        
        Returns:
            str: The file tag.
        """
        pass


    @abstractmethod
    def get_gpt_embedding_key(self) -> str:
        """
        Retrieve the embedding key used for the custom GPT instance.
        
        Returns:
            str: The embedding key.
        """
        pass
