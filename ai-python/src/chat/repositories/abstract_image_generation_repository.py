from abc import ABC, abstractmethod

class ImageGenerationAbstractRepository(ABC):
    """Abstract base class for image generation"""
    @abstractmethod
    def initialize_llm_tool(self, api_key_id: str = None, companymodel: str = None):
        """
        Initializes the LLM with the specified API key and company model.

        Parameters
        ----------
        api_key_id : str, optional
            The API key ID used for decryption and initialization.
        companymodel : str, optional
            The company model configuration for the LLM.

        Exceptions
        ----------
        Logs an error if the initialization fails.
        """
        pass
    @abstractmethod
    def initialize_repository(self, chat_session_id: str = None, collection_name: str = None):
        """
        Initializes the chat history repository for data storage.

        Parameters
        ----------
        chat_session_id : str, optional
            The chat session ID for the repository.
        collection_name : str, optional
            The collection name for the repository.

        Exceptions
        ----------
        Logs an error if the repository initialization fails.
        """
        pass

    @abstractmethod
    def initialize_memory(self):
        """
        Sets up the memory component using ConversationSummaryBufferMemory.

        Exceptions
        ----------
        Logs an error if the memory initialization fails.
        """
        pass


    @abstractmethod
    def create_conversation(self, input_text:str=None,**kwargs):
        """
        Creates a conversation chain with a custom tag.

        Parameters
        ----------
        input_text : str
            Input given by the user.
        
        

        Exceptions
        ----------
        Logs an error if the conversation creation fails.
        """
        pass

    @abstractmethod
    def save_image_to_db(self,s3_file_name,thread_id,collection_name):
        """
        Saves the generated image into Database

        Parameters
        ----------
        s3_file_name:str
            Name of the file that is stored in s4
        thread_id : ID of the thread
        collection_name : str, optional
            The collection name for the repository.

        """
        pass

    @abstractmethod
    async def run_image_generation(self,thread_id: str, collection_name: str,**kwargs):
        """
        Runs the image generation chain and gives image url as response

        Parameters
        ----------
        thread_id : ID of the thread
        collection_name : str, optional
            The collection name for the repository.
        
        """
        pass