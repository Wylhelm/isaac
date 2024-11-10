"""
Database models for the test scenario generator application.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import JSON
import numpy as np
import json
from config import logger

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
    
    __tablename__ = 'test_scenario'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    criteria = db.Column(db.Text, nullable=False)
    scenario = db.Column(db.Text, nullable=False)
    statistics = db.Column(db.Text, nullable=True)
    uploaded_files = db.Column(db.Text, nullable=True)
    vector_embedding = db.Column(db.Text, nullable=True)  # Stored as JSON string of embedding vector
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    def set_vector_embedding(self, embedding: np.ndarray):
        """Store numpy array as JSON string."""
        if embedding is not None:
            try:
                self.vector_embedding = json.dumps(embedding.tolist())
            except Exception as e:
                logger.error(f"Error setting vector embedding: {str(e)}")
                self.vector_embedding = None
    
    def get_vector_embedding(self) -> np.ndarray:
        """Retrieve vector embedding as numpy array."""
        if self.vector_embedding:
            try:
                return np.array(json.loads(self.vector_embedding))
            except Exception as e:
                logger.error(f"Error getting vector embedding: {str(e)}")
                return None
        return None

    def __repr__(self):
        return f'<TestScenario {self.id}: {self.name}>'

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
    
    __tablename__ = 'document_chunk'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    chunk_metadata = db.Column(JSON, nullable=False)  # Renamed from metadata to chunk_metadata
    vector_embedding = db.Column(db.Text, nullable=False)  # Stored as JSON string
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    def set_vector_embedding(self, embedding: np.ndarray):
        """Store numpy array as JSON string."""
        if embedding is not None:
            try:
                self.vector_embedding = json.dumps(embedding.tolist())
            except Exception as e:
                logger.error(f"Error setting vector embedding: {str(e)}")
                self.vector_embedding = None
    
    def get_vector_embedding(self) -> np.ndarray:
        """Retrieve vector embedding as numpy array."""
        if self.vector_embedding:
            try:
                return np.array(json.loads(self.vector_embedding))
            except Exception as e:
                logger.error(f"Error getting vector embedding: {str(e)}")
                return None
        return None

    def __repr__(self):
        return f'<DocumentChunk {self.id}>'

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
    
    __tablename__ = 'document'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    chunks = db.relationship('DocumentChunk', backref='document', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Document {self.id}: {self.filename}>'

def init_db(app):
    """Initialize the database with the Flask application context."""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Created tables: {', '.join(tables)}")
            
            # Log table schemas
            for table_name in tables:
                columns = [col['name'] for col in inspector.get_columns(table_name)]
                logger.info(f"Table {table_name} columns: {', '.join(columns)}")
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
