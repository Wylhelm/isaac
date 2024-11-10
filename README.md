![ISAAC](static/images/isaac.png)

# Intelligent Scenarios Automated Assessment Creator

## Overview
ISAAC is an AI-powered web application designed to assist testers and QA professionals in creating comprehensive test scenarios. It leverages Retrieval Augmented Generation (RAG) and a local Large Language Model (LLM) to analyze documents and generate contextually relevant test scenarios that adhere to the IEEE 829 standard.

## Key Features
- Advanced RAG-based document analysis and scenario generation
- Support for multiple file formats:
  - Documents: PDF, Word (DOCX), Text files
  - Images: PNG, JPG, JPEG (with AI-powered image analysis)
- Vector-based document storage for intelligent context retrieval
- Scenario-isolated vector stores for better context management
- Streaming response generation with real-time output
- Customizable system prompts and scenario templates
- Adjustable context window size (4096 or 8192 tokens)
- Batch processing capabilities for multiple files
- Real-time inference statistics
- Export functionality for generated scenarios
- Comprehensive scenario history management

## Project Structure
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

## Installation
1. Ensure Python 3.7+ is installed on your system.
2. Clone this repository:
   ```
   git clone https://github.com/Wylhelm/qa-ai-super.git
   ```
3. Navigate to the project directory:
   ```
   cd qa-ai-super
   ```
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Set up a local LLM server (e.g., using LM Studio) accessible at http://localhost:1234

## Configuration
1. Copy `.env.example` to `.env` and configure:
   - LLM server settings
   - Vector store parameters
   - Chunk size and overlap
   - Maximum relevant chunks for RAG
   - Context window size

## Usage
1. Start the application:
   ```
   python app.py
   ```
2. Open a web browser and navigate to `http://localhost:5000`
3. Upload documents or enter test criteria
4. The system will:
   - Process and analyze documents using RAG
   - Store document vectors for context retrieval
   - Generate contextually relevant test scenarios
   - Provide real-time generation progress and statistics

## Requirements
- Python 3.7+
- Flask and Flask-SQLAlchemy
- langchain and langchain-community
- HuggingFace Transformers
- ChromaDB for vector storage
- Document processing libraries:
  - PyPDF2
  - python-docx
  - Pillow
  - pytesseract
- Local LLM server (e.g., LM Studio)

## Documentation
- `user_guide.md` - Comprehensive user instructions
- `developer_guide.md` - Technical documentation and API reference

## Contributing
Contributions are welcome! Please read our contributing guidelines for details on submitting pull requests.

## License
This project is licensed under the GPL-3.0 license. See the `LICENSE` file for details.

## Acknowledgments
- CGI Innovation and Immersive Systems Community
- HuggingFace for embeddings models
- ChromaDB for vector storage capabilities

For detailed usage instructions, see `user_guide.md`.
