# Pinecone and Celery Task Development Summary

## Pinecone Index Creation
- Created Pinecone service with both serverless index and pod-based index.
- Built an application for creating Pinecone indexes.
- Developed a dynamic class for initializing the Pinecone index.
- Created a GCP starter free Pinecone instance.

## Celery Tasks
- Developed a Celery task for upserting embedded nodes.
- Researched how to resolve dependency conflicts between Ray and the Pinecone client.
- Developed independent task execution with Celery in different queues to handle dependency issues.

## Pinecone Parallel Insertion and Testing
- Implemented parallel insertion with a 30-thread pool for faster insertions.
- Added parallel insertion functionality for Pinecone insertion.
- Tested the pipeline for inserting vectors, encountering and resolving issues with formatting and vector insertion.
- Performed test cases with varying sizes of data (in MB) pushed to Pinecone.

## Other Research
- Conducted research on FastAPI background tasks.
- Stored results on Redis to enable an independent FastAPI service.
- Researched Redis Pub/Sub event listeners.
- Investigated Pinecone pricing with the new calculator (1 hour).
