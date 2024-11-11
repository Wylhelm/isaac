"""
RAG components for enhanced document processing and scenario generation.
"""

import os
import time
import json
import requests
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

def calculate_mmr(
    query_embedding: np.ndarray,
    embeddings: List[np.ndarray],
    lambda_param: float = 0.5,
    k: int = 5
) -> List[int]:
    """
    Calculate Maximum Marginal Relevance (MMR) for diversity in retrieval.
    
    Args:
        query_embedding: Query embedding
        embeddings: List of document embeddings
        lambda_param: Trade-off between relevance and diversity (0-1)
        k: Number of documents to select
        
    Returns:
        List of selected indices
    """
    selected_indices = []
    remaining_indices = list(range(len(embeddings)))
    
    # Convert embeddings to numpy arrays if they aren't already
    embeddings = [np.array(emb) if not isinstance(emb, np.ndarray) else emb 
                 for emb in embeddings]
    
    for _ in range(min(k, len(embeddings))):
        if not remaining_indices:
            break
            
        # Calculate relevance scores
        relevance_scores = [
            np.dot(query_embedding, embeddings[idx]) /
            (np.linalg.norm(query_embedding) * np.linalg.norm(embeddings[idx]))
            for idx in remaining_indices
        ]
        
        if not selected_indices:
            # First selection based on relevance only
            best_idx = remaining_indices[np.argmax(relevance_scores)]
        else:
            # Calculate diversity scores
            diversity_scores = []
            for idx, rel_score in zip(remaining_indices, relevance_scores):
                # Calculate similarity to already selected documents
                similarities = [
                    np.dot(embeddings[idx], embeddings[sel_idx]) /
                    (np.linalg.norm(embeddings[idx]) * np.linalg.norm(embeddings[sel_idx]))
                    for sel_idx in selected_indices
                ]
                diversity = min(1 - max(similarities))
                mmr_score = lambda_param * rel_score + (1 - lambda_param) * diversity
                diversity_scores.append(mmr_score)
            
            best_idx = remaining_indices[np.argmax(diversity_scores)]
        
        selected_indices.append(best_idx)
        remaining_indices.remove(best_idx)
    
    return selected_indices

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
        
        # Add source tracking metadata
        for i, metadata in enumerate(metadatas):
            if 'source' not in metadata:
                metadata['source'] = f'Document_{i+1}'
        
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        # Force persistence after adding
        self.vector_store.persist()
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform similarity search with MMR for diversity within scenario context.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        try:
            # Get query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Get all potentially relevant documents
            filter_dict = {'scenario_id': self.scenario_id} if self.scenario_id else None
            results = self.vector_store.similarity_search_with_score(
                query, 
                k=k*2,  # Get more candidates for MMR
                filter=filter_dict
            )
            
            if not results:
                return []
            
            # Separate documents and scores
            docs, scores = zip(*results)
            
            # Get document embeddings
            doc_embeddings = [
                self.embeddings.embed_query(doc.page_content)
                for doc in docs
            ]
            
            # Apply MMR
            selected_indices = calculate_mmr(
                query_embedding,
                doc_embeddings,
                k=k
            )
            
            # Return selected documents
            return [docs[i] for i in selected_indices]
            
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
        """Process file into chunks with embeddings and enhanced metadata."""
        try:
            # Extract filename for source tracking
            filename = os.path.basename(file_path)
            file_type = os.path.splitext(filename)[1].lower()
            
            # For image files, use the analysis from the Document model
            if file_type in ['.png', '.jpg', '.jpeg']:
                from models import Document
                doc = Document.query.filter_by(file_path=file_path).first()
                if doc and doc.image_analysis:
                    metadata = {
                        'type': 'visual_test_elements',
                        'source': filename,
                        'content_type': 'image_analysis'
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
            
            # Process chunks with enhanced metadata
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                # Get embedding
                embedding = self.vector_store.embed_query(chunk.page_content)
                
                # Create metadata with enhanced tracking
                metadata = {
                    'source': filename,
                    'type': 'document',
                    'content_type': file_type.replace('.', ''),
                    'page': chunk.metadata.get('page', 0),
                    'chunk_index': i,
                    'total_chunks': len(chunks)
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

class BatchProcessor:
    """Handles batch processing of multiple files."""
    
    def __init__(self, scenario_id: Optional[int] = None):
        self.scenario_id = scenario_id
        self.document_processor = EnhancedDocumentProcessor(scenario_id)
    
    async def process_batch(self, file_paths: List[str], batch_size: int = 5):
        """Process files in batches with enhanced progress tracking."""
        try:
            total_chunks = 0
            total_files = len(file_paths)
            
            for i in range(0, total_files, batch_size):
                batch = file_paths[i:i + batch_size]
                processed_chunks = []
                
                # Process batch
                for file_path in batch:
                    chunks = self.document_processor.process_file(file_path)
                    processed_chunks.extend(chunks)
                    total_chunks += len(chunks)
                
                yield {
                    'batch_index': i // batch_size,
                    'processed_files': len(batch),
                    'total_chunks': len(processed_chunks),
                    'cumulative_chunks': total_chunks,
                    'progress_percentage': ((i + len(batch)) / total_files) * 100
                }
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise

class EnhancedScenarioGenerator:
    """Enhanced scenario generator using RAG with scenario isolation."""
    
    def __init__(self, scenario_id: Optional[int] = None):
        self.scenario_id = scenario_id
        self.vector_store = VectorStoreManager(scenario_id)
    
    def format_context(self, relevant_docs):
        """Format retrieved documents into structured context with source tracking."""
        if not relevant_docs:
            return "No relevant context found in the document collection."
        
        formatted_contexts = []
        for i, doc in enumerate(relevant_docs, 1):
            # Extract source information from metadata
            source = doc.metadata.get('source', f'Document {i}')
            doc_type = doc.metadata.get('type', 'Unknown')
            page = doc.metadata.get('page', 'N/A')
            
            # Format context with clear section markers and metadata
            context_block = f"""
[DOCUMENT {i}]
Source: {source}
Type: {doc_type}
Page/Section: {page}
Content:
{doc.page_content}
---"""
            formatted_contexts.append(context_block)
        
        return "\n\n".join(formatted_contexts)
    
    def validate_context_usage(self, generated_text, context_docs):
        """Validate that the generated scenario actually uses the provided context."""
        if not context_docs:
            return False, "No context documents were provided for validation"
        
        # Extract key phrases from context
        key_phrases = set()
        for doc in context_docs:
            # Split content into words and get phrases of 3-4 words
            words = doc.page_content.split()
            for i in range(len(words)-2):
                key_phrases.add(" ".join(words[i:i+3]))
        
        # Check for presence of key phrases in generated text
        matches = 0
        for phrase in key_phrases:
            if phrase in generated_text:
                matches += 1
        
        # Calculate coverage ratio
        coverage_ratio = matches / len(key_phrases) if key_phrases else 0
        
        # Validate document references
        has_doc_refs = any(f"[Doc " in generated_text or f"[DOCUMENT " in generated_text)
        
        if coverage_ratio < 0.1 or not has_doc_refs:  # Less than 10% coverage
            return False, "Generated scenario doesn't sufficiently incorporate context"
        
        return True, f"Context integration validated (Coverage: {coverage_ratio:.2%})"
    
    def generate_scenario_stream(self, criteria: str):
        """Generate a test scenario using streaming response with RAG."""
        # Get relevant context using RAG with MMR diversity
        relevant_docs = self.vector_store.similarity_search(
            criteria,
            k=Config.MAX_RELEVANT_CHUNKS
        )
        
        # Format context with clear structure and source tracking
        context = self.format_context(relevant_docs)
        
        url = "http://localhost:1234/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        
        # Enhanced prompt combining system and scenario prompts
        combined_prompt = f"{Config.SYSTEM_PROMPT}\n\n{Config.SCENARIO_PROMPT.format(context=context, criteria=criteria)}"
        
        data = {
            "model": "local-model",
            "messages": [
                {"role": "user", "content": combined_prompt}
            ],
            "max_tokens": Config.CONTEXT_WINDOW_SIZE,
            "stream": True
        }
        
        start_time = time.time()
        input_tokens = len(combined_prompt.split())
        output_tokens = 0
        scenario = ""
        
        try:
            response = requests.post(url, headers=headers, json=data, stream=True)
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            line_text = line.decode('utf-8')
                            if line_text.startswith('data: '):
                                json_str = line_text[6:]  # Remove 'data: ' prefix
                                json_object = json.loads(json_str)
                                if 'choices' in json_object and len(json_object['choices']) > 0:
                                    delta = json_object['choices'][0]['delta']
                                    if 'content' in delta:
                                        content = delta['content']
                                        output_tokens += len(content.split())
                                        scenario += content
                                        yield content
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse JSON: {line_text}")
                        except Exception as e:
                            logger.error(f"Error processing line: {str(e)}")
                
                # Validate context usage
                is_valid, validation_msg = self.validate_context_usage(scenario, relevant_docs)
                
                end_time = time.time()
                generation_time = end_time - start_time
                
                # Enhanced statistics with validation results
                statistics = (
                    f"\n\nInference Statistics:"
                    f"\nInput Tokens: {input_tokens}"
                    f"\nOutput Tokens: {output_tokens}"
                    f"\nGeneration Time: {generation_time:.2f} seconds"
                    f"\nRetrieved Contexts: {len(relevant_docs)}"
                    f"\nContext Validation: {validation_msg}"
                )
                
                # If validation failed, append warning
                if not is_valid:
                    statistics += "\n\n⚠️ WARNING: The generated scenario may not sufficiently incorporate the provided context documents. Please review and regenerate if necessary."
                
                yield statistics
            else:
                error_msg = f"Error generating scenario: HTTP {response.status_code}"
                logger.error(error_msg)
                yield error_msg
        except Exception as e:
            error_msg = f"Error in generate_scenario_stream: {str(e)}"
            logger.error(error_msg)
            yield error_msg
