# Developer Guide for ISAAC

## Introduction
ISAAC (Intelligent Scenarios Automated Assessment Creator) is an AI-powered web application designed to assist testers and QA professionals in creating comprehensive test scenarios. It leverages Retrieval Augmented Generation (RAG) and a local Large Language Model (LLM) to analyze documents and generate contextually relevant test scenarios that adhere to the IEEE 829 standard.

## Project Setup

### Prerequisites
- Ensure Python 3.10+ is installed on your system.
- Set up a local LLM server (e.g., using LM Studio) accessible at http://localhost:1234.

### Environment Setup
It is recommended to use a virtual environment to manage dependencies and avoid conflicts. You can use either Python's built-in `venv` module or Conda.

#### Using Python's `venv`
1. Create a virtual environment:
   ```
   python3 -m venv env
   ```
2. Activate the virtual environment:
   - On macOS and Linux:
     ```
     source env/bin/activate
     ```
   - On Windows:
     ```
     .\env\Scripts\activate
     ```

#### Using Conda
1. Create a Conda environment:
   ```
   conda create --name isaac_env python=3.10
   ```
2. Activate the Conda environment:
   ```
   conda activate isaac_env
   ```

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/Wylhelm/isaac.git
   ```
2. Navigate to the project directory:
   ```
   cd isaac
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure:
   - LLM server settings
   - Vector store parameters
   - Chunk size and overlap
   - Maximum relevant chunks for RAG
   - Context window size

## Architecture Overview
The application follows a modular architecture:
- `app.py` - Main Flask application and server initialization
- `config.py` - Configuration management and environment settings
- `models.py` - Database models and data structures
- `rag_components.py` - RAG implementation and vector store management
- `file_processor.py` - Enhanced document processing and analysis
- `scenario_generator.py` - LLM-based scenario generation with streaming
- `routes.py` - API endpoints and route handlers
- `templates/` - HTML templates for the web interface
- `static/` - Static assets (CSS, JS, images)
- `vector_store/` - Persistent storage for document vectors

## Key Components
- **RAG Components**: Handles document analysis and scenario generation.
- **Vector Store**: Manages document vectors for context retrieval.
- **Scenario Generator**: Utilizes LLM for generating test scenarios.

## Development Practices
- Follow PEP 8 coding standards for Python code.
- Write unit tests for new features and bug fixes.
- Document code using docstrings and comments.
- Use Git for version control and create feature branches for new developments.

## API Reference
- **Endpoints**: Defined in `routes.py`, providing access to scenario generation and document processing functionalities.

## Troubleshooting
- Ensure all dependencies are installed correctly.
- Verify the LLM server is running and accessible.
- Check `.env` configuration for any misconfigurations.

## Additional Resources
- Refer to `user_guide.md` for comprehensive user instructions.
- Explore the `README.md` for an overview and installation guide.

## Contributing
Contributions are welcome! Please read our contributing guidelines for details on submitting pull requests.

## License
This project is licensed under the GPL-3.0 license. See the `LICENSE` file for details.

## Acknowledgments
- CGI Innovation and Immersive Systems Community
- HuggingFace for embeddings models
- ChromaDB for vector storage capabilities
