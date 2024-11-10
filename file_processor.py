"""
File processing module for handling various file types and image analysis.
"""

import os
from werkzeug.utils import secure_filename
from datetime import datetime
from models import Document, db
from rag_components import EnhancedDocumentProcessor
from config import Config, logger

def process_file(file, app):
    """
    Process uploaded files using RAG components.
    
    Args:
        file: File object from request
        app: Flask application instance
    
    Returns:
        dict: Dictionary containing filename and processing results
    """
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Create document record
        file_type = os.path.splitext(filename)[1][1:].lower()
        document = Document(
            filename=filename,
            file_type=file_type,
            upload_date=datetime.now()
        )
        db.session.add(document)
        db.session.commit()

        # Process document using RAG
        processor = EnhancedDocumentProcessor()
        chunks = processor.process_file(filepath)

        return {
            'filename': filename,
            'chunks_processed': len(chunks),
            'document_id': document.id
        }
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {'filename': filename, 'error': str(e)}
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
