# RAG Implementation and Optimization Guide for Isaac

## Current System Limitations
1. Sequential file processing without chunking
2. In-memory processing of all content
3. No vector embeddings or semantic search
4. Limited scalability for large document sets
5. Files are processed and discarded

## Proposed RAG Architecture

### 1. Vector Database Integration
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# Store vectors persistently
VECTOR_DB_PATH = "vector_store"
embeddings = OpenAIEmbeddings()
vector_store = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
```

### 2. Document Processing Pipeline
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredImageLoader
)

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
    def process_document(self, file_path):
        # Select appropriate loader
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        elif file_path.endswith('.txt'):
            loader = TextLoader(file_path)
        elif file_path.endswith(('.png', '.jpg', '.jpeg')):
            loader = UnstructuredImageLoader(file_path)
        
        # Load and chunk document
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        
        # Store in vector database
        vector_store.add_documents(chunks)
        
        return len(chunks)
```

### 3. Enhanced Scenario Generation
```python
class ScenarioGenerator:
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    def generate_scenario(self, criteria, k=5):
        # Retrieve relevant chunks
        relevant_docs = self.vector_store.similarity_search(criteria, k=k)
        
        # Construct enhanced prompt
        context = "\n".join([doc.page_content for doc in relevant_docs])
        enhanced_prompt = f"""
        Based on the following context and criteria, generate a test scenario:
        
        Context:
        {context}
        
        Criteria:
        {criteria}
        """
        
        # Generate scenario using enhanced prompt
        return generate_with_context(enhanced_prompt)
```

### 4. Caching Layer
```python
from functools import lru_cache
import hashlib

class CacheManager:
    @lru_cache(maxsize=1000)
    def get_cached_embeddings(self, content):
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return self.vector_store.get(content_hash)
```

## Implementation Steps

1. Database Schema Updates:
- Add vector embeddings column to TestScenario model
- Create new table for document chunks
- Add metadata for document relationships

2. File Processing Optimization:
- Implement batch processing for multiple files
- Add progress tracking for large uploads
- Store processed chunks in vector database
- Maintain file references instead of content

3. Retrieval Enhancement:
- Implement semantic search using embeddings
- Add relevance scoring
- Support filtering by document type/source

4. Performance Monitoring:
- Add telemetry for processing times
- Track vector store query performance
- Monitor memory usage

## Configuration Updates

Update config.py to include:
```python
class Config:
    # Existing configs...
    
    # Vector Store Configuration
    VECTOR_DB_PATH = "vector_store"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Retrieval Configuration
    MAX_RELEVANT_CHUNKS = 5
    SIMILARITY_THRESHOLD = 0.7
    
    # Cache Configuration
    CACHE_SIZE = 1000
    CACHE_TTL = 3600  # 1 hour
```

## Benefits

1. Improved Scalability:
- Efficient handling of large document sets
- Reduced memory usage through chunking
- Better resource utilization

2. Enhanced Retrieval:
- Semantic search capabilities
- More relevant context for scenario generation
- Faster query response times

3. Better Performance:
- Cached results for frequent queries
- Optimized document processing
- Reduced API calls

4. Maintainability:
- Structured document processing pipeline
- Clear separation of concerns
- Easy to extend and modify

## Next Steps

1. Implement the vector database integration
2. Update the document processing pipeline
3. Enhance the scenario generation with RAG
4. Add caching layer
5. Update tests and documentation
6. Monitor performance and adjust parameters

This implementation will significantly improve the system's ability to handle large amounts of documents and images while maintaining performance and reliability.
