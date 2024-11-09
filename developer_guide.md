# Developer Guide

## RAG (Retrieval Augmented Generation) Implementation

### Overview
The system uses RAG to enhance scenario generation by leveraging existing documents and historical scenarios. This implementation includes:

1. Vector Database Integration
- Uses Chroma for vector storage
- HuggingFace embeddings (all-MiniLM-L6-v2 model)
- Persistent storage in `vector_store/` directory

2. Document Processing Pipeline
- Chunking with RecursiveCharacterTextSplitter
- Support for PDF, DOCX, TXT, and image files
- Metadata preservation and chunk relationships

3. Enhanced Scenario Generation
- Context-aware generation using relevant document chunks
- Semantic search for finding similar scenarios
- Batch processing capabilities

### Database Schema

#### TestScenario Model
- Added vector embeddings for semantic search
- Stores embeddings as JSON-serialized numpy arrays
- Methods for embedding manipulation

#### Document Model
- Tracks uploaded documents
- Maintains relationships with chunks
- Stores metadata about document source

#### DocumentChunk Model
- Stores processed document chunks
- Contains vector embeddings for search
- Links back to source document

### Performance Monitoring

The monitoring system tracks:

1. Vector Store Performance
```python
from monitoring import vector_metrics

# Track query performance
with vector_metrics.track_query("search query", num_results=5) as ctx:
    # Perform vector store query
    results = vector_store.similarity_search(query)

# Get performance metrics
metrics = vector_metrics.get_metrics_summary()
```

2. System Resources
```python
from monitoring import monitor

@monitor.track_operation("custom_operation")
def your_function():
    # Function implementation
    pass

# Get overall metrics
summary = monitor.get_metrics_summary()
```

Metrics tracked include:
- Query response times
- Embedding generation times
- Memory usage
- CPU utilization
- Index size and growth

### Testing

Run tests using pytest:
```bash
pytest tests/
```

#### Test Coverage
- Vector store operations
- Document processing
- Scenario generation
- Batch processing
- Performance monitoring

#### Adding New Tests
1. Create test files in `tests/` directory
2. Use appropriate fixtures from `conftest.py`
3. Follow existing patterns for consistency

Example:
```python
def test_vector_store_query():
    # Arrange
    store = VectorStoreManager()
    query = "test query"
    
    # Act
    results = store.similarity_search(query)
    
    # Assert
    assert len(results) > 0
```

### Best Practices

1. Document Processing
- Use appropriate chunk sizes (default: 1000 chars)
- Maintain chunk overlap (default: 200 chars)
- Preserve document metadata

2. Vector Store Operations
- Monitor index size growth
- Implement regular maintenance
- Use batch operations for efficiency

3. Performance Optimization
- Cache frequently accessed embeddings
- Use batch processing for multiple documents
- Monitor and adjust chunk sizes based on performance

4. Error Handling
- Implement proper exception handling
- Log errors with context
- Maintain data consistency

### Deployment Considerations

1. Vector Store
- Ensure sufficient storage for vector database
- Monitor index size growth
- Plan for backup and recovery

2. Resource Requirements
- CPU: Sufficient for embedding generation
- Memory: Depends on chunk size and concurrent operations
- Storage: Vector store + document storage

3. Scaling
- Monitor performance metrics
- Adjust chunk sizes and batch processing
- Consider distributed processing for large datasets

### Troubleshooting

1. Vector Store Issues
- Check persistence directory permissions
- Verify embedding dimensions
- Monitor index corruption

2. Performance Issues
- Review monitoring metrics
- Adjust chunk sizes
- Check resource utilization

3. Memory Management
- Monitor memory usage patterns
- Implement batch processing
- Clean up unused resources

### Future Improvements

1. Planned Enhancements
- Distributed vector store support
- Advanced caching mechanisms
- Real-time performance dashboards

2. Optimization Opportunities
- Embedding model optimization
- Chunk size auto-tuning
- Advanced query optimization

### Contributing

1. Code Style
- Follow PEP 8 guidelines
- Add appropriate docstrings
- Include type hints

2. Testing
- Write tests for new features
- Maintain test coverage
- Include performance tests

3. Documentation
- Update developer guide
- Document API changes
- Include example usage

### API Reference

1. VectorStoreManager
```python
class VectorStoreManager:
    def add_chunks(self, chunks: List[ProcessedChunk]) -> None
    def similarity_search(self, query: str, k: int = 5) -> List[Dict]
```

2. EnhancedDocumentProcessor
```python
class EnhancedDocumentProcessor:
    def process_file(self, file_path: str) -> List[ProcessedChunk]
    def get_loader(self, file_path: str) -> BaseLoader
```

3. Performance Monitoring
```python
class PerformanceMonitor:
    def track_operation(self, operation_name: str)
    def get_metrics_summary() -> Dict[str, Any]
```

### Environment Setup

1. Requirements
```bash
pip install -r requirements.txt
```

2. Environment Variables
```bash
VECTOR_DB_PATH=vector_store
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

3. Database Initialization
```python
from models import init_db
init_db(app)
