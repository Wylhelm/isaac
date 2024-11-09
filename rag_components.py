"""
RAG components for enhanced document processing and scenario generation.
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import (
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
    """Manages vector storage operations."""
    
    def __init__(self):
        # Use HuggingFace embeddings instead of OpenAI
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"  # Lightweight, efficient model
        )
        self.vector_store = Chroma(
            persist_directory=Config.VECTOR_DB_PATH,
            embedding_function=self.embeddings
        )
    
    def add_chunks(self, chunks: List[ProcessedChunk]):
        """Add document chunks to vector store."""
        texts = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Perform similarity search for query."""
        return self.vector_store.similarity_search(query, k=k)

class EnhancedDocumentProcessor:
    """Enhanced document processor with chunking and embedding."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        self.vector_store = VectorStoreManager()
    
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
            # Load document
            loader = self.get_loader(file_path)
            documents = loader.load()
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Process chunks
            processed_chunks = []
            for chunk in chunks:
                embedding = self.vector_store.embeddings.embed_query(chunk.page_content)
                processed_chunk = ProcessedChunk(
                    content=chunk.page_content,
                    metadata={
                        'source': file_path,
                        'page': chunk.metadata.get('page', 0),
                        'chunk_index': len(processed_chunks)
                    },
                    embedding=embedding
                )
                processed_chunks.append(processed_chunk)
            
            # Store in vector database
            self.vector_store.add_chunks(processed_chunks)
            
            return processed_chunks
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

class EnhancedScenarioGenerator:
    """Enhanced scenario generator using RAG."""
    
    def __init__(self):
        self.vector_store = VectorStoreManager()
    
    def generate_scenario(self, criteria: str) -> str:
        """Generate scenario using RAG approach."""
        try:
            # Get relevant chunks
            relevant_docs = self.vector_store.similarity_search(
                criteria,
                k=Config.MAX_RELEVANT_CHUNKS
            )
            
            # Build context from relevant chunks
            context = "\n".join([
                f"Context {i+1}:\n{doc.page_content}\n"
                for i, doc in enumerate(relevant_docs)
            ])
            
            # Enhance prompt with context
            enhanced_prompt = Config.SCENARIO_PROMPT.format(
                criteria=f"""
                Using the following context and criteria, generate a detailed test scenario.
                
                {context}
                
                Criteria:
                {criteria}
                """
            )
            
            # Generate scenario using enhanced prompt
            from scenario_generator import generate_scenario_stream
            return generate_scenario_stream(enhanced_prompt)
        except Exception as e:
            logger.error(f"Error generating scenario: {str(e)}")
            raise

class BatchProcessor:
    """Handles batch processing of multiple files."""
    
    def __init__(self):
        self.document_processor = EnhancedDocumentProcessor()
    
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
