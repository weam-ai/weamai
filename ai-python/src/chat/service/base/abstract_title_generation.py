from abc import ABC, abstractmethod

class AbstractTitleGeneration(ABC):
    """
    Abstract base class for managing conversations.

    Methods
    -------
    initialize_llm(api_key_id: str = None, companymodel: str = None)
        Initializes the LLM (Language Learning Model) with the given API key and company model.
        
    initialize_thread_data(thread_id: str = None, collection_name: str = None)
        Initializes the chat history repository for data storage and sets up the memory component.
        
    create_prompt()
        Creates a conversation chain with a custom prompt.
        
    create_chain()
        Sets up the conversation chain with the LLM and prompt, and initializes the output parser.
        
    update_chat_session_title(chat_session_id: str = None, title: str = None, collection_name: str = None)
        Updates the chat session title in the repository.
        
    update_token_usage(cb, tokens_old)
        Updates the token usage data in the repository.
        
    run_chain(chat_session_id: str = None, collection_name: str = None)
        Executes a conversation, updates the token usage, and stores the conversation history.
    """

    @abstractmethod
    def initialize_llm(self, api_key_id: str = None, companymodel: str = None):
        """
        Initializes the LLM with the specified API key and company model.
        
        Parameters
        ----------
        api_key_id : str, optional
            The API key ID used for decryption and initialization.
        companymodel : str, optional
            The company model configuration for the LLM.
        """
        pass

    @abstractmethod
    def initialize_thread_data(self, thread_id: str = None, collection_name: str = None):
        """
        Initializes the chat history repository for data storage.
        
        Parameters
        ----------
        thread_id : str, optional
            The thread ID for the repository.
        collection_name : str, optional
            The collection name for the repository.
        """
        pass

    @abstractmethod
    def create_prompt(self):
        """
        Creates a conversation chain with a custom prompt.
        """
        pass

    @abstractmethod
    def create_chain(self):
        """
        Sets up the conversation chain with the LLM and prompt, and initializes the output parser.
        """
        pass

    @abstractmethod
    def update_chat_session_title(self, chat_session_id: str = None, title: str = None, collection_name: str = None):
        """
        Updates the chat session title in the repository.
        
        Parameters
        ----------
        chat_session_id : str
            The ID of the chat session.
        title : str
            The new title for the chat session.
        collection_name : str
            The collection name for the repository.
        """
        pass

    @abstractmethod
    def update_token_usage(self, cb, tokens_old):
        """
        Updates the token usage data in the repository.
        
        Parameters
        ----------
        cb : Callback
            The callback object containing token usage information.
        tokens_old : dict
            The old token usage data.
        """
        pass

    @abstractmethod
    def run_chain(self, chat_session_id: str = None, collection_name: str = None):
        """
        Executes a conversation and updates the token usage and conversation history.
        
        Returns
        -------
        tuple
            A tuple containing the response and the callback data.
        """
        pass
