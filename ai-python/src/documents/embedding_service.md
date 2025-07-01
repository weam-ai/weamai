

# Text Embedding Service Model Class Development

## Overview
The project involves creating a generalized embedding model class that can process input text and produce corresponding vector embeddings. This class should be flexible to support multiple embedding models and integrate with various technologies like Pinecone, Hugging Face, Celery, FastAPI, and Ray.

### Key Components

1. **Generalized Embedding Model Class**
   - Develop a class for generating text embeddings.
   - Ensure the class can transform data and push vectors to the Pinecone service.

2. **Integration of Multiple Hugging Face Models**
   - Integrate 2-3 different Hugging Face models within the embedding class.
   - Provide flexibility in choosing the model based on specific requirements.

3. **OpenAI Model Embedding Integration**
   - Build embedding capabilities using OpenAI models within the class.

4. **Celery Task Management**
   - Create a Celery task based on parameters to determine which embedding pipeline to use.

5. **FastAPI Application Development For Hugging Face Model**
   - Develop a FastAPI application that interfaces with the Ray system.
   - Retrieve computed embedding vectors from Ray object references.

6. **Offloading Computation to Ray**
   - Utilize Ray containers to offload computational workload.
   - Implement dynamic batch-wise vector embedding to optimize resource usage and processing time.
   - This Task is Still In Developement Face

7. **GPU Allocation Research in Ray**
   - Research how GPU resources are allocated and managed within the Ray ecosystem.
   - Optimize the processing of embedding vectors based on the findings.
