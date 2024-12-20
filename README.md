![Test Scenario Generator](static/images/appbanner.png)

# Test Scenario Generator

## Overview
The Test Scenario Generator is an AI-powered web application designed to assist testers and QA professionals in creating comprehensive test scenarios. It analyzes documents (Word, PDF, text files, and images) to generate scenarios that adhere to the IEEE 829 standard, leveraging a local Large Language Model (LLM) for AI capabilities.

## Key Features
- Document analysis (Word, PDF, text files, and images)
- AI-powered test scenario generation using a local LLM
- Web-based user interface for easy access
- Scenario history management and storage
- File upload and processing
- Customizable system prompt and scenario prompt
- Adjustable context window size
- Real-time scenario generation with stop functionality
- Clear scenario history option
- Export generated scenarios
- Inference statistics display

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

## Usage
1. Set up your environment variables in a `.env` file (see `.env.example` for reference)
2. Run the application:
   ```
   python app.py
   ```
3. Open a web browser and navigate to `http://localhost:5000`
4. Follow the on-screen instructions to create and generate test scenarios.

## Requirements
- Python 3.7+
- Flask
- Flask-SQLAlchemy
- docx2txt
- PyPDF2
- Pillow
- pytesseract
- requests
- python-dotenv
- Local LLM server (e.g., using LM Studio) accessible at http://localhost:1234

## Contributing
Contributions are welcome! Please read the contributing guidelines in `CONTRIBUTING.md` for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the GPL-3.0 license. See the `LICENSE` file for details.

## Acknowledgments
- CGI Innovation and Immersive Systems Community

For more information, please refer to the `user_guide.md` for usage instructions and `developer_guide.md` for development details.
