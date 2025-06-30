from abc import ABC, abstractmethod


class AbstractConversationService(ABC):
    @abstractmethod
    def initialize_llm(self):
        """
        Initialize the specific language model used for generating responses.
        This should configure the model with necessary parameters such as API keys, model settings, and any other required configuration.
        """
        pass

    @abstractmethod
    def initialize_repository(self):
        """
        Initialize the data repository used for storing conversation history.
        This can involve setting up connections to databases or configuring file-based storage systems, depending on the implementation specifics.
        """
        pass

    @abstractmethod
    def initialize_memory(self):
        """
        Set up the in-memory data structure or service used for temporary storage of conversation state.
        This may involve initializing buffers, caches, or other temporary storage mechanisms to hold the current state of the conversation.
        """
        pass


    @abstractmethod
    def create_conversation(self):
        """
        Create and initialize a new conversation instance.
        This could involve setting up conversation parameters, selecting prompts, or other preparatory steps necessary before starting a conversation.
        """
        pass
    
    
