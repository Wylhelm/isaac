"""
Configuration settings for the application.
"""

import os
import logging
from datetime import datetime

# Get absolute path to project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configuration class for the application."""
    
    # Basic Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Database Configuration
    INSTANCE_PATH = os.path.join(PROJECT_ROOT, 'instance')
    DB_NAME = 'isaac.db'
    DB_PATH = os.path.join(INSTANCE_PATH, DB_NAME)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # RAG Configuration
    VECTOR_DB_PATH = os.path.join(PROJECT_ROOT, "vector_store")
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    MAX_RELEVANT_CHUNKS = 5
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Prompt Templates
    SYSTEM_PROMPT = """You are a test scenario generator that creates comprehensive test scenarios based on given context and criteria."""
    
    SCENARIO_PROMPT = """Based on the following context and criteria, generate a detailed test scenario and ensure the scenario adheres to the IEEE 829 standard for test documentation.:
    
    Context:
    {context}
    
    Criteria:
    {criteria}
    
    Please provide a comprehensive test scenario that includes:

    1. Ignore all filenames and add the Test Scenario ID and Name
    2. Test Case Objective
    3. Preconditions
    4. Test Steps (including inputs and expected results)
    5. Post-conditions
    6. Test Data Requirements
    7. Environmental Needs
    8. Any special procedural requirements
    9. Inter-case dependencies (if applicable)
    10. Actions and expected results
    11. At the end write "Created by CGI Innovation and Immersive Systems Community"
    """
    
    # Context Window Configuration
    CONTEXT_WINDOW_SIZE = 8192

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S%f'
)
logger = logging.getLogger('config')

# Ensure required directories exist with proper permissions
required_dirs = [
    Config.UPLOAD_FOLDER,
    Config.VECTOR_DB_PATH,
    Config.INSTANCE_PATH
]

for directory in required_dirs:
    if not os.path.exists(directory):
        os.makedirs(directory, mode=0o755)
        logger.info(f"Created directory with permissions: {directory}")
    else:
        # Update permissions if directory exists
        os.chmod(directory, 0o755)
        logger.info(f"Updated permissions for directory: {directory}")

# Create empty database file if it doesn't exist
if not os.path.exists(Config.DB_PATH):
    try:
        with open(Config.DB_PATH, 'w') as f:
            pass  # Create empty file
        os.chmod(Config.DB_PATH, 0o644)  # Set file permissions
        logger.info(f"Created database file: {Config.DB_PATH}")
    except Exception as e:
        logger.error(f"Error creating database file: {str(e)}")

# Initialize vector store directory with a .gitkeep file
vector_store_gitkeep = os.path.join(Config.VECTOR_DB_PATH, '.gitkeep')
if not os.path.exists(vector_store_gitkeep):
    with open(vector_store_gitkeep, 'w') as f:
        f.write(f'# Vector store directory\n# Created: {datetime.now().isoformat()}')
    logger.info("Created .gitkeep in vector store directory")

# Create .gitignore if it doesn't exist
gitignore_path = os.path.join(PROJECT_ROOT, '.gitignore')
gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Project specific
uploads/
vector_store/
*.db
.env
"""

if not os.path.exists(gitignore_path):
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content.strip())
    logger.info("Created .gitignore file")
