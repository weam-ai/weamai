from abc import ABC, abstractmethod
import torch
import numpy as np
from abc import ABCMeta, abstractmethod
from transformers import AutoModel, AutoTokenizer

# Creating a combined metaclass inheriting from both ABCMeta and type (for Singleton)
class CombinedMeta(ABCMeta, type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Ensure that the creation respects ABCMeta and Singleton behavior
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

# Use CombinedMeta as the metaclass for the abstract class
class AbstractEmbeddings(ABC):
    def __init__(self, model_name, use_gpu=True,batch_size=100):
        self.device = "cuda" if torch.cuda.is_available() and use_gpu else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.batch_size=batch_size

    @abstractmethod
    def embed_documents(self, texts):
        pass

class HuggingFaceEmbeddings(AbstractEmbeddings):
    def embed_documents(self, texts):
        self.model.eval()
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i+self.batch_size]
            with torch.no_grad():
                encoded_input = self.tokenizer(batch_texts, padding=True, truncation=True, return_tensors='pt').to(self.device)
                output = self.model(**encoded_input)
                embeddings.append(output.last_hidden_state.mean(dim=1).cpu().numpy())
        return np.concatenate(embeddings, axis=0)

