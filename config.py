"""
Configuration module for the test scenario generator application.
Contains all configuration variables and environment setup.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)
logger = logging.getLogger(__name__)

# Application configuration
class Config:
    """Configuration class holding all application settings."""
    
    # Flask configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///scenarios.db'
    UPLOAD_FOLDER = 'uploads'
    
    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # API configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
    
    # Prompt configuration
    SYSTEM_PROMPT = "You are a test scenario generator that creates comprehensive test scenarios based on given criteria."
    CONTEXT_WINDOW_SIZE = 4096
    SCENARIO_PROMPT = """Generate a test scenario based on the following criteria:

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

Ensure the scenario adheres to the IEEE 829 standard for test documentation."""
