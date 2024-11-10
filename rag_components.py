"""
RAG components for enhanced document processing and scenario generation.
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredImageLoader
)
from config import Config, logger

@dataclass
class ProcessedChunk:
    """Represents a processed document chunk with metadata."""
    content: str
    metadata: Dict[str, Any]
    embedding: np.ndarray

class VectorStoreManager:
    """Manages vector storage operations with scenario isolation."""
    
    def __init__(self, scenario_id: Optional[int] = None):
        self.scenario_id = scenario_id
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Create scenario-specific persist directory if scenario_id is provided
        persist_dir = Config.VECTOR_DB_PATH
        if scenario_id:
            persist_dir = os.path.join(persist_dir, f"scenario_{scenario_id}")
        
        # Ensure directory exists
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize vector store
        try:
            self.vector_store = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings
            )
            # Force initialization of collections
            self.vector_store.get()
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            # If initialization fails, create a new store
            if os.path.exists(persist_dir):
                import shutil
                shutil.rmtree(persist_dir)
                os.makedirs(persist_dir)
            self.vector_store = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings
            )
    
    def add_chunks(self, chunks: List[ProcessedChunk]):
        """Add document chunks to vector store with scenario isolation."""
        if not chunks:
            return
        
        texts = [chunk.content for chunk in chunks]
        metadatas = [
            {**chunk.metadata, 'scenario_id': self.scenario_id} 
            for chunk in chunks
        ]
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        # Force persistence after adding
        self.vector_store.persist()
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Perform similarity search within scenario context."""
        try:
            filter_dict = {'scenario_id': self.scenario_id} if self.scenario_id else None
            results = self.vector_store.similarity_search(
                query, 
                k=k,
                filter=filter_dict
            )
            return results if results else []
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    def embed_query(self, text: str) -> np.ndarray:
        """Get embedding for text."""
        try:
            embedding = self.embeddings.embed_query(text)
            if isinstance(embedding, list):
                embedding = np.array(embedding)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return np.zeros(384)  # Default embedding dimension for all-MiniLM-L6-v2
    
    @classmethod
    def cleanup_scenario_vectors(cls, scenario_id: int):
        """Clean up vector store for a specific scenario."""
        scenario_dir = os.path.join(Config.VECTOR_DB_PATH, f"scenario_{scenario_id}")
        if os.path.exists(scenario_dir):
            import shutil
            shutil.rmtree(scenario_dir)
            logger.info(f"Cleaned up vector store for scenario {scenario_id}")

class EnhancedDocumentProcessor:
    """Enhanced document processor with chunking and embedding."""
    
    def __init__(self, scenario_id: Optional[int] = None):
        self.scenario_id = scenario_id
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        self.vector_store = VectorStoreManager(scenario_id)
    
    def get_loader(self, file_path: str):
        """Get appropriate document loader based on file type."""
        ext = os.path.splitext(file_path)[1].lower()
        loaders = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.txt': TextLoader,
            '.png': UnstructuredImageLoader,
            '.jpg': UnstructuredImageLoader,
            '.jpeg': UnstructuredImageLoader
        }
        loader_class = loaders.get(ext)
        if not loader_class:
            raise ValueError(f"Unsupported file type: {ext}")
        return loader_class(file_path)
    
    def process_file(self, file_path: str) -> List[ProcessedChunk]:
        """Process file into chunks with embeddings."""
        try:
            # For image files, we'll use the analysis directly from the Document model
            if any(file_path.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                from models import Document
                doc = Document.query.filter_by(file_path=file_path).first()
                if doc and doc.image_analysis:
                    metadata = {
                        'type': 'test_scenario_content',
                        'content_type': 'visual_test_elements'
                    }
                    embedding = self.vector_store.embed_query(doc.image_analysis)
                    
                    chunk = ProcessedChunk(
                        content=doc.image_analysis,
                        metadata=metadata,
                        embedding=embedding
                    )
                    # Immediately add to vector store
                    self.vector_store.add_chunks([chunk])
                    return [chunk]
                return []
            
            # For other document types, process normally
            loader = self.get_loader(file_path)
            documents = loader.load()
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Process chunks
            processed_chunks = []
            for chunk in chunks:
                # Get embedding
                embedding = self.vector_store.embed_query(chunk.page_content)
                
                # Create metadata with scenario context
                metadata = {
                    'type': 'document',
                    'page': chunk.metadata.get('page', 0),
                    'chunk_index': len(processed_chunks)
                }
                if self.scenario_id:
                    metadata['scenario_id'] = self.scenario_id
                
                processed_chunk = ProcessedChunk(
                    content=chunk.page_content,
                    metadata=metadata,
                    embedding=embedding
                )
                processed_chunks.append(processed_chunk)
            
            # Store in vector database
            if processed_chunks:
                self.vector_store.add_chunks(processed_chunks)
            
            return processed_chunks
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return []

class EnhancedScenarioGenerator:
    """Enhanced scenario generator using RAG with scenario isolation."""
    
    def __init__(self, scenario_id: Optional[int] = None):
        self.scenario_id = scenario_id
        self.vector_store = VectorStoreManager(scenario_id)
    
    def generate_scenario(self, criteria: str) -> str:
        """Generate scenario using RAG approach with scenario isolation."""
        try:
            # Get relevant chunks for this scenario only
            relevant_docs = self.vector_store.similarity_search(
                criteria,
                k=Config.MAX_RELEVANT_CHUNKS
            )
            
            # Build context from relevant chunks
            context_parts = []
            for doc in relevant_docs:
                # Handle test scenario content (including image analysis)
                if doc.metadata.get('type') == 'test_scenario_content':
                    context_parts.append(doc.page_content)
                else:
                    # For other documents, include minimal metadata
                    context_parts.append(f"Document Content (Page {doc.metadata.get('page', 0)}):\n{doc.page_content}")
            
            context = "\n\n".join(context_parts) if context_parts else "No relevant context found."
            
            # Format prompt with context and criteria
            prompt_template = Config.SCENARIO_PROMPT.replace(
                "{context}", context
            ).replace(
                "{criteria}", criteria
            )
            
            # Generate scenario using the formatted prompt
            from scenario_generator import generate_scenario_stream
            return generate_scenario_stream(prompt_template)
            
        except Exception as e:
            logger.error(f"Error generating scenario: {str(e)}")
            return f"Error generating scenario: {str(e)}"

class BatchProcessor:
    """Handles batch processing of multiple files."""
    
    def __init__(self, scenario_id: Optional[int] = None):
        self.scenario_id = scenario_id
        self.document_processor = EnhancedDocumentProcessor(scenario_id)
    
    async def process_batch(self, file_paths: List[str], batch_size: int = 5):
        """Process files in batches."""
        try:
            for i in range(0, len(file_paths), batch_size):
                batch = file_paths[i:i + batch_size]
                processed_chunks = []
                
                # Process batch
                for file_path in batch:
                    chunks = self.document_processor.process_file(file_path)
                    processed_chunks.extend(chunks)
                
                yield {
                    'batch_index': i // batch_size,
                    'processed_files': len(batch),
                    'total_chunks': len(processed_chunks)
                }
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise
