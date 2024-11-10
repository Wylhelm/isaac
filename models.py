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
    """
    
    __tablename__ = 'test_scenario'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    criteria = db.Column(db.Text, nullable=False)
    scenario = db.Column(db.Text, nullable=False)
    statistics = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    # Relationships
    documents = db.relationship('Document', secondary='scenario_document_association',
                              backref=db.backref('scenarios', lazy='dynamic'))
    
    def __repr__(self):
        return f'<TestScenario {self.id}: {self.name}>'

class Document(db.Model):
    """
    Document model representing an uploaded document.
    """
    
    __tablename__ = 'document'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=True)  # Store text content for text-based files
    image_analysis = db.Column(db.Text, nullable=True)  # Store image analysis results
    file_path = db.Column(db.String(255), nullable=False)  # Store actual file path
    upload_date = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    
    # Relationships
    chunks = db.relationship('DocumentChunk', backref='document', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Document {self.id}: {self.filename}>'

class DocumentChunk(db.Model):
    """
    DocumentChunk model representing a processed chunk of a document.
    """
    
    __tablename__ = 'document_chunk'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    chunk_metadata = db.Column(JSON, nullable=False)
    vector_embedding = db.Column(db.Text, nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey('test_scenario.id'), nullable=True)  # Link to specific scenario
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

# Association table for many-to-many relationship between scenarios and documents
scenario_document_association = db.Table('scenario_document_association',
    db.Column('scenario_id', db.Integer, db.ForeignKey('test_scenario.id'), primary_key=True),
    db.Column('document_id', db.Integer, db.ForeignKey('document.id'), primary_key=True)
)

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
