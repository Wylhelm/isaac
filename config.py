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
    SYSTEM_PROMPT = """You are a test scenario generator that creates comprehensive test scenarios based on given context and criteria. Your role is to analyze the provided content and generate relevant test scenarios that verify the described elements, relationships, and requirements."""
    
    SCENARIO_PROMPT = """Based on the following context and criteria, generate a detailed test scenario that adheres to the IEEE 829 standard for test documentation. The scenario should be specifically tailored to verify and validate the described content, whether it's a process flow, architecture, UI, diagram, or any other type of content.
    
    Context:
    {context}
    
    Criteria:
    {criteria}
    
    Generate a comprehensive test scenario that includes:

    1. Test Scenario ID and Name:
       - Should reflect the specific aspect being tested
       - Must be based on the actual content described, not file metadata
    
    2. Test Case Objective:
       - Clear goal derived from the analyzed content
       - Focus on what needs to be verified or validated
    
    3. Preconditions:
       - Required initial state
       - Any necessary setup or prerequisites
    
    4. Test Steps:
       - Detailed steps specific to the content type
       - For UI: Include user interactions and validations
       - For diagrams/flows: Include process verification steps
       - For architecture: Include component verification
       - Clear expected results for each step
    
    5. Post-conditions:
       - Expected state after test execution
       - Required cleanup or reset steps
    
    6. Test Data Requirements:
       - Specific data needed for testing
       - Data validation points
    
    7. Environmental Needs:
       - Required systems or components
       - Configuration requirements
    
    8. Special Procedural Requirements:
       - Any specific testing approaches needed
       - Timing or sequence dependencies
    
    9. Inter-case Dependencies:
       - Related test cases or prerequisites
       - Impact on other components or processes
    
    10. Pass/Fail Criteria:
        - Clear success criteria
        - Specific validation points
    
    11. Created by CGI Innovation and Immersive Systems Community
    """
    
    # Context Window Configuration
    CONTEXT_WINDOW_SIZE = 8192

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
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
