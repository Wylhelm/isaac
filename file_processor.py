"""
File processing module for handling various file types and image analysis.
"""

import os
import docx2txt
import PyPDF2
from PIL import Image
import pytesseract
import requests
import json
from werkzeug.utils import secure_filename
from config import Config, logger

def process_file(file, app):
    """
    Process uploaded files and extract their content.
    
    Args:
        file: File object from request
        app: Flask application instance
    
    Returns:
        dict: Dictionary containing filename and extracted content
    """
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if filename.endswith('.docx'):
            content = docx2txt.process(filepath)
        elif filename.endswith('.pdf'):
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                content = ' '.join([page.extract_text() for page in reader.pages])
        elif filename.endswith('.txt'):
            with open(filepath, 'r') as f:
                content = f.read()
        elif filename.endswith(('.png', '.jpg', '.jpeg')):
            content = analyze_image(filepath)
        else:
            content = ''

        return {'filename': filename, 'content': content}
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {'filename': filename, 'content': ''}
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

def analyze_image(image_path):
    """
    Analyze image content using OCR and OpenAI API.
    
    Args:
        image_path (str): Path to the image file
    
    Returns:
        str: Analyzed content from the image
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)

        api_key = Config.OPENAI_API_KEY
        if not api_key:
            return "Error: OpenAI API key not found in environment variables"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": Config.OPENAI_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": f"Provide a detailed description of the following text extracted from an image: {text}"
                }
            ],
            "max_tokens": 1000
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response_data = response.json()

        if response.status_code == 200:
            return response_data['choices'][0]['message']['content']
        else:
            logger.error(f"Error analyzing image: {response_data}")
            return "Error analyzing image"
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return "Error processing image"
