"""
File processing module for handling various file types and image analysis.
"""

import os
import shutil
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from models import Document, DocumentChunk, db
from rag_components import EnhancedDocumentProcessor
from config import Config, logger
import base64
from PIL import Image
import io
from openai import OpenAI

def ensure_upload_dir(upload_folder):
    """Ensure upload directory exists with proper structure."""
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    return upload_folder

def get_permanent_path(upload_folder, filename, timestamp):
    """Generate a permanent file path using timestamp to prevent naming conflicts."""
    base, ext = os.path.splitext(filename)
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    permanent_filename = f"{base}_{timestamp_str}{ext}"
    return os.path.join(upload_folder, permanent_filename)

def analyze_image(image_path):
    """
    Analyze image using OpenAI's vision model.
    Returns detailed description of image content.
    """
    try:
        # Initialize OpenAI client
        client = OpenAI()
        
        # Read and encode image
        with open(image_path, "rb") as image_file:
            # Convert image to base64
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            image_url = f"data:image/jpeg;base64,{image_data}"

        # Create message for analysis with specific focus on test scenarios
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a test scenario expert. Your task is to analyze the content shown in images and describe it in a way that enables testing of the actual system or process being depicted. 

For example:
- If you see a website/application interface, describe the actual functionality and interactions that need to be tested in the live system
- If you see a process diagram, describe the actual process steps and validations needed
- If you see an architecture diagram, describe the actual components and integrations to be tested

Never treat the content as just an image to be viewed - always focus on testing the actual system or process shown."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze what is shown in this image and describe:

1. What system, process, or concept is being shown?
2. What are the key elements that need to be tested?
3. What functionality or behaviors need to be verified?
4. What are the important validation points?
5. What specific interactions or flows need to be tested?

Important: Focus on describing how to test the actual system/process shown, not the image itself. For example:
- Don't say "verify the image shows a login form"
- Instead say "verify the login form accepts valid credentials and validates input"

Describe everything in terms of actual testing actions on the live system."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
        )

        # Extract and clean the response content
        analysis = response.choices[0].message.content
        
        # Remove any mentions of filenames or image references
        import re
        analysis = re.sub(r'\b\w+\.(png|jpg|jpeg)\b', '', analysis, flags=re.IGNORECASE)
        analysis = re.sub(r'(?i)\b(image|file|screenshot)\b', '', analysis)
        analysis = re.sub(r'\s+', ' ', analysis).strip()
        
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return f"Error analyzing image: {str(e)}"

def process_file(file, app, scenario_id=None):
    """
    Process uploaded files using RAG components.
    
    Args:
        file: File object from request
        app: Flask application instance
        scenario_id: Optional ID of the scenario this file is associated with
    
    Returns:
        dict: Dictionary containing filename and processing results
    """
    temp_path = None
    try:
        filename = secure_filename(file.filename)
        file_type = os.path.splitext(filename)[1][1:].lower()
        upload_time = datetime.now()
        
        # Create permanent path using timestamp
        permanent_path = get_permanent_path(app.config['UPLOAD_FOLDER'], filename, upload_time)
        
        # Save file to temporary location first
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
        file.save(temp_path)
        
        # Move to permanent location
        shutil.move(temp_path, permanent_path)
        temp_path = None  # Clear temp_path as file has been moved
        
        # Create document record with file_path
        document = Document(
            filename=filename,
            file_type=file_type,
            file_path=permanent_path,
            upload_date=upload_time
        )
        
        # Process based on file type
        if file_type.lower() in ['png', 'jpg', 'jpeg']:
            # Process image
            image_analysis = analyze_image(permanent_path)
            document.image_analysis = image_analysis
            # Store analysis directly without any file references
            document.content = image_analysis
        
        # Add document to database to get ID
        db.session.add(document)
        db.session.commit()
        
        # Process document using RAG if it's not an image or if it has analysis
        if document.content:  # Either text content or image analysis
            processor = EnhancedDocumentProcessor(scenario_id)
            chunks = processor.process_file(permanent_path)
            
            # Store chunks with scenario association if provided
            for chunk in chunks:
                # For image analysis, ensure the chunk metadata indicates test-relevant content
                if file_type.lower() in ['png', 'jpg', 'jpeg']:
                    chunk_metadata = {
                        'type': 'test_scenario_content',
                        'content_type': 'system_test_elements',
                        'analysis_timestamp': upload_time.isoformat()
                    }
                else:
                    chunk_metadata = chunk.metadata

                doc_chunk = DocumentChunk(
                    content=chunk.content,
                    chunk_metadata=chunk_metadata,
                    document_id=document.id,
                    scenario_id=scenario_id
                )
                doc_chunk.set_vector_embedding(chunk.embedding)
                db.session.add(doc_chunk)
            
            db.session.commit()

        return {
            'filename': filename,
            'document_id': document.id,
            'file_type': file_type,
            'chunks_processed': len(document.chunks) if hasattr(document, 'chunks') else 0,
            'has_image_analysis': bool(document.image_analysis)
        }
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        # Clean up temporary file if it exists
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return {'filename': filename if 'filename' in locals() else 'unknown', 'error': str(e)}

def cleanup_old_files(app, days_old=7):
    """
    Clean up files older than specified days that are not associated with any scenario.
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Find documents to delete
        old_docs = Document.query.filter(
            Document.upload_date < cutoff_date,
            ~Document.scenarios.any()  # No associated scenarios
        ).all()
        
        for doc in old_docs:
            # Remove physical file
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
            
            # Remove database record
            db.session.delete(doc)
        
        db.session.commit()
        logger.info(f"Cleaned up {len(old_docs)} old files")
    except Exception as e:
        logger.error(f"Error cleaning up old files: {str(e)}")
        db.session.rollback()
