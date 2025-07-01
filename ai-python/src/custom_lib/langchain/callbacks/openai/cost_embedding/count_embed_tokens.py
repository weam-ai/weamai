import tiktoken
MODEL_PER_1K_TOKENS = {
    "text-embedding-3-small":0.00002,
    "text-embedding-3-large":0.00013,
}
class CostEmbedding():
    def __init__(self,encoding = 'cl100k_base'):
      self.encoding = encoding

    def count_token_chunks(self,chunked_data):
        try:
            encoding = tiktoken.get_encoding(self.encoding)
            total_vectors=len(chunked_data)
            chunked_data = ''.join(chunked_data)
            num_tokens = len(encoding.encode(chunked_data))
        finally:
            for var in ['encoding', 'chunked_data']:
                if var in locals():
                    del locals()[var]
                    
        return num_tokens,total_vectors
    
    def calculate_cost_for_embedding(self,chunked_data,model_name):
        num_tokens,total_vectors = self.count_token_chunks(chunked_data)
        cost = (num_tokens/1000)*MODEL_PER_1K_TOKENS[model_name]
        token_data = {
              "$set": {
                        "tokens.totalUsed": num_tokens,
                        "tokens.embedT": num_tokens,
                        "tokens.totalCost": cost,
                        "total_vectors":total_vectors
                    }
        }
        return token_data