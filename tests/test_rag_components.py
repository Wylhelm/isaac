"""
Tests for RAG components functionality.
"""

import unittest
import numpy as np
import os
import sys
import json
import tempfile
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_components import (
    VectorStoreManager,
    EnhancedDocumentProcessor,
    EnhancedScenarioGenerator,
    BatchProcessor,
    ProcessedChunk
)
from models import TestScenario, DocumentChunk, Document, db
from config import Config

class TestVectorStoreManager(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for vector store
        self.temp_dir = tempfile.mkdtemp()
        Config.VECTOR_DB_PATH = self.temp_dir
        self.vector_store = VectorStoreManager()

    def tearDown(self):
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_add_chunks(self):
        # Create test chunks
        chunks = [
            ProcessedChunk(
                content="Test content 1",
                metadata={"source": "test1.txt"},
                embedding=np.array(np.random.rand(384))  # Ensure numpy array
            ),
            ProcessedChunk(
                content="Test content 2",
                metadata={"source": "test2.txt"},
                embedding=np.array(np.random.rand(384))
            )
        ]
        
        # Add chunks to vector store
        self.vector_store.add_chunks(chunks)
        
        # Verify chunks were added by performing a search
        results = self.vector_store.similarity_search("Test content", k=2)
        self.assertEqual(len(results), 2)

    def test_similarity_search(self):
        # Add test data
        test_chunks = [
            ProcessedChunk(
                content="Python programming language",
                metadata={"source": "test.txt"},
                embedding=np.array(np.random.rand(384))
            ),
            ProcessedChunk(
                content="JavaScript web development",
                metadata={"source": "test.txt"},
                embedding=np.array(np.random.rand(384))
            )
        ]
        self.vector_store.add_chunks(test_chunks)
        
        # Test search
        results = self.vector_store.similarity_search("Python", k=1)
        self.assertEqual(len(results), 1)

class TestEnhancedDocumentProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = EnhancedDocumentProcessor()
        self.test_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        with open(self.test_file.name, 'w') as f:
            f.write("Test content for document processing.")

    def tearDown(self):
        os.unlink(self.test_file.name)

    def test_get_loader(self):
        # Test loader selection for different file types
        self.assertRaises(ValueError, self.processor.get_loader, "invalid.xyz")
        loader = self.processor.get_loader(self.test_file.name)
        self.assertIsNotNone(loader)

    def test_process_file(self):
        # Process test file
        chunks = self.processor.process_file(self.test_file.name)
        self.assertGreater(len(chunks), 0)
        self.assertIsInstance(chunks[0], ProcessedChunk)
        self.assertIsInstance(chunks[0].embedding, np.ndarray)

class TestEnhancedScenarioGenerator(unittest.TestCase):
    @patch('rag_components.VectorStoreManager')
    def setUp(self, mock_vector_store):
        self.generator = EnhancedScenarioGenerator()
        self.mock_vector_store = mock_vector_store.return_value
        
        # Mock search results
        self.mock_vector_store.similarity_search.return_value = [
            Mock(page_content="Test context 1"),
            Mock(page_content="Test context 2")
        ]

    def test_generate_scenario(self):
        criteria = "Generate a test scenario for login functionality"
        # Collect all generated content from the stream
        scenario_stream = self.generator.generate_scenario(criteria)
        scenario = "".join([chunk for chunk in scenario_stream])
        
        # Verify vector store was queried
        self.mock_vector_store.similarity_search.assert_called_once()
        
        # Verify scenario was generated
        self.assertIsInstance(scenario, str)
        self.assertGreater(len(scenario), 0)

class TestBatchProcessor:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.processor = BatchProcessor()
        self.test_files = []
        
        # Create test files
        for i in range(3):
            temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
            with open(temp_file.name, 'w') as f:
                f.write(f"Test content {i}")
            self.test_files.append(temp_file.name)
        
        yield
        
        # Cleanup
        for file_path in self.test_files:
            os.unlink(file_path)

    @pytest.mark.asyncio
    async def test_process_batch(self):
        batch_results = []
        async for result in self.processor.process_batch(self.test_files, batch_size=2):
            batch_results.append(result)
        
        # Verify batch processing results
        assert len(batch_results) == 2  # Should have 2 batches for 3 files with batch_size=2
        assert 'processed_files' in batch_results[0]
        assert 'total_chunks' in batch_results[0]

class TestModels(unittest.TestCase):
    def setUp(self):
        # Create test app context
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()

    def test_test_scenario_model(self):
        with self.app.app_context():
            # Create test scenario
            scenario = TestScenario(
                name="Test Login",
                criteria="Test login functionality",
                scenario="Login test steps...",
                statistics="Test stats",
                uploaded_files="file1.txt,file2.txt"
            )
            
            # Test vector embedding
            embedding = np.array(np.random.rand(384))
            scenario.set_vector_embedding(embedding)
            
            db.session.add(scenario)
            db.session.commit()
            
            # Verify retrieval
            retrieved = TestScenario.query.first()
            self.assertEqual(retrieved.name, "Test Login")
            np.testing.assert_array_almost_equal(
                retrieved.get_vector_embedding(),
                embedding
            )

    def test_document_chunk_model(self):
        with self.app.app_context():
            # Create document
            doc = Document(
                filename="test.txt",
                file_type="text",
                upload_date=datetime.now()
            )
            db.session.add(doc)
            db.session.commit()
            
            # Create chunk
            chunk = DocumentChunk(
                content="Test content",
                chunk_metadata={"page": 1, "position": "top"},
                vector_embedding=json.dumps(np.array(np.random.rand(384)).tolist()),
                document_id=doc.id
            )
            db.session.add(chunk)
            db.session.commit()
            
            # Verify retrieval
            retrieved = DocumentChunk.query.first()
            self.assertEqual(retrieved.content, "Test content")
            self.assertEqual(retrieved.chunk_metadata["page"], 1)
            self.assertIsInstance(retrieved.get_vector_embedding(), np.ndarray)

if __name__ == '__main__':
    unittest.main()
