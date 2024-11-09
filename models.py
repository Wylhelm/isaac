"""
Database models for the test scenario generator application.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import JSON
import numpy as np
import json

db = SQLAlchemy()

class TestScenario(db.Model):
    """
    TestScenario model representing a generated test scenario.
    
    Attributes:
        id (int): Primary key
        name (str): Name of the test scenario
        criteria (str): Input criteria used to generate the scenario
        scenario (str): Generated scenario content
        statistics (str): Generation statistics
        uploaded_files (str): List of files used in generation
        vector_embedding (str): JSON string of vector embedding for semantic search
    """
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    criteria = db.Column(db.Text, nullable=False)
    scenario = db.Column(db.Text, nullable=False)
    statistics = db.Column(db.Text)
    uploaded_files = db.Column(db.Text)
    vector_embedding = db.Column(db.Text)  # Stored as JSON string of embedding vector
    
    def set_vector_embedding(self, embedding: np.ndarray):
        """Store numpy array as JSON string."""
        self.vector_embedding = json.dumps(embedding.tolist())
    
    def get_vector_embedding(self) -> np.ndarray:
        """Retrieve vector embedding as numpy array."""
        if self.vector_embedding:
            return np.array(json.loads(self.vector_embedding))
        return None

class DocumentChunk(db.Model):
    """
    DocumentChunk model representing a processed chunk of a document.
    
    Attributes:
        id (int): Primary key
        content (str): The text content of the chunk
        chunk_metadata (JSON): Metadata about the chunk (source file, page number, etc.)
        vector_embedding (str): JSON string of vector embedding for semantic search
        document_id (int): Foreign key to parent Document
    """
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    chunk_metadata = db.Column(JSON, nullable=False)  # Renamed from metadata to chunk_metadata
    vector_embedding = db.Column(db.Text, nullable=False)  # Stored as JSON string
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    
    def set_vector_embedding(self, embedding: np.ndarray):
        """Store numpy array as JSON string."""
        self.vector_embedding = json.dumps(embedding.tolist())
    
    def get_vector_embedding(self) -> np.ndarray:
        """Retrieve vector embedding as numpy array."""
        return np.array(json.loads(self.vector_embedding))

class Document(db.Model):
    """
    Document model representing an uploaded document.
    
    Attributes:
        id (int): Primary key
        filename (str): Original filename
        file_type (str): Type of document (PDF, DOCX, etc.)
        upload_date (DateTime): When the document was uploaded
        chunks (relationship): One-to-many relationship with DocumentChunk
    """
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False)
    chunks = db.relationship('DocumentChunk', backref='document', lazy=True)

def init_db(app):
    """Initialize the database with the Flask application context."""
    with app.app_context():
        db.create_all()
