from abc import ABC, abstractmethod

class LanguageModelFactory(ABC):
    @abstractmethod
    def create_language_model(self, **kwargs):
        pass
