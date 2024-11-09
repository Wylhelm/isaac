# Test Scenario Generator - Developer Guide

## Project Overview 
The Test Scenario Generator is a Flask-based web application that leverages AI to analyze documents (Word, PDF, text files, and images) to automatically generate comprehensive test scenarios. It uses a local Large Language Model (LLM) to create scenarios adhering to the IEEE 829 standard.

## Project Structure
The application is organized into modular components for better maintainability:

- `app.py`: Main application initialization and configuration
- `config.py`: Configuration management and environment setup
- `models.py`: Database models and initialization
- `file_processor.py`: File processing and image analysis logic
- `scenario_generator.py`: Test scenario generation functionality
- `routes.py`: Flask route handlers and API endpoints
- `templates/index.html`: HTML template for the main user interface
- `static/`: Directory for static files (CSS, JavaScript, images)
- `.env`: Environment variables file (not in version control)
- `requirements.txt`: List of Python dependencies
- `README.md`: Project overview and setup instructions
- `user_guide.md`: User guide for the application
- `developer_guide.md`: This file, containing development details

## Setup and Dependencies
1. Ensure Python 3.7+ is installed.
2. Install dependencies: `pip install -r requirements.txt`
3. Set up a local LLM server (e.g., using LM Studio) accessible at http://localhost:1234.
4. Create a `.env` file with necessary environment variables (see `.env` section in this guide).

## Key Components

### Main Application (app.py)
- Creates and configures the Flask application
- Initializes database and extensions
- Registers routes and blueprints

### Configuration (config.py)
- Manages application configuration and environment variables
- Sets up logging configuration
- Defines system prompts and default settings

### Database Models (models.py)
- Defines the TestScenario model using SQLAlchemy
- Handles database initialization and management
- Provides database utility functions

### File Processing (file_processor.py)
- Processes various file types (DOCX, PDF, TXT, PNG, JPG, JPEG)
- Implements image analysis using OpenAI's API
- Handles file uploads and content extraction

### Scenario Generation (scenario_generator.py)
- Manages communication with local LLM server
- Handles scenario generation and streaming
- Provides prompt management functionality

### Route Handlers (routes.py)
- Implements all Flask routes and API endpoints
- Handles HTTP requests and responses
- Manages application flow and business logic

### User Interface (templates/index.html)
- Provides a responsive web interface
- Implements client-side functionality using JavaScript
- Handles real-time scenario generation display

## Environment Variables (.env)
The application uses the following environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key for image analysis
- `OPENAI_MODEL`: The OpenAI model to use (default: gpt-4o)
- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `DATABASE_URI`: SQLite database URI
- `LOCAL_LLM_SERVER_URL`: URL of the local LLM server
- `DEBUG`: Debug mode flag (True/False)

## Workflow
1. User creates a new scenario with an automatically assigned name.
2. Documents are uploaded and processed by file_processor.py.
3. Extracted information is added to the criteria input.
4. User can modify the criteria if needed.
5. User can customize system prompt, scenario prompt, and context window size.
6. scenario_generator.py generates a test scenario using the local LLM server.
7. Generated scenario is displayed in real-time, with the option to stop generation.
8. Completed scenario is saved to the database and can be exported.
9. Inference statistics are displayed after generation.

## Extending the Application
- To add new file types, extend the process_file function in file_processor.py
- To modify the UI, update the index.html template and associated JavaScript
- To change the database schema, update the TestScenario model in models.py
- To add new features, create new routes in routes.py and corresponding UI elements

## Best Practices
- Follow PEP 8 style guidelines for Python code
- Write unit tests for new features (use unittest or pytest)
- Document new methods and functions using docstrings
- Handle exceptions appropriately and provide user-friendly error messages
- Use environment variables for sensitive information and configuration
- Implement proper error handling for asynchronous operations
- Regularly update dependencies and check for security vulnerabilities

## Troubleshooting
- Ensure the local LLM server is running and accessible at http://localhost:1234
- Check the server logs for error messages and stack traces
- Ensure all required dependencies are installed and up to date
- Verify that the context window size is appropriate for the chosen LLM model
- Debug frontend issues using browser developer tools and console logs
- For OpenAI API issues, check your API key and quota

## Recent Improvements
- Refactored application into modular components for better maintainability
- Added proper documentation for all modules and functions
- Improved error handling and logging across all components
- Centralized configuration management
- Added real-time scenario generation with stop functionality
- Implemented customizable scenario prompt
- Added clear history functionality
- Improved UI responsiveness and feedback
- Integrated OpenAI API for image analysis
- Added support for multiple file uploads
- Implemented inference statistics display

## Future Improvements
- Implement user authentication and multi-user support
- Add support for more file formats and AI models
- Add the possibility to be integrated to other applications (ex:Jira)
- Enhance the UI with more interactive features and real-time updates
- Implement a plugin system for easy extension of file processing capabilities
- Add a feature to compare and merge multiple scenarios
- Implement automated testing for both backend and frontend components
- Improve error handling and user feedback for LLM server connection issues
- Add support for different LLM providers and models
- Implement a feature to save and load custom prompt templates
- Add pagination for scenario history to improve performance with large datasets
- Enhance the filtering and sorting system for scenarios

For any questions or contributions, please contact the project maintainers.
