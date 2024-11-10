# ISAAC - User Guide

## Introduction
ISAAC is an AI-powered web application that uses Retrieval Augmented Generation (RAG) to create comprehensive test scenarios. It intelligently analyzes documents and images to generate contextually relevant scenarios that adhere to the IEEE 829 standard, leveraging a local Large Language Model (LLM) for AI capabilities.

## Getting Started
1. Ensure the application is running and accessible (typically at http://localhost:5000)
2. Open your web browser and navigate to the application URL
3. You'll see the main interface with file upload capabilities, input areas, and scenario history

## Document Processing Features

### Supported File Types
- Documents:
  - PDF files (.pdf)
  - Word documents (.docx)
  - Text files (.txt)
- Images:
  - PNG files (.png)
  - JPEG files (.jpg, .jpeg)

### Uploading Documents
1. Click the "Upload Document" button
2. Select one or more supported files
3. The system will:
   - Process each document using RAG technology
   - Extract and analyze content
   - Store document vectors for intelligent retrieval
   - For images: perform AI-powered analysis to extract relevant test elements
4. Progress indicators will show processing status
5. Processed content will be available for context-aware scenario generation

## Creating Test Scenarios

### Basic Scenario Creation
1. Click "Create New Scenario"
2. Enter a scenario name (or use the auto-generated name)
3. Input test criteria in the criteria text area
4. Click "Generate Scenario"

### Enhanced RAG Features
- The system will:
  - Retrieve relevant context from processed documents
  - Use vector similarity to find related content
  - Generate scenarios based on combined context
  - Show real-time generation progress
  - Display inference statistics

### Batch Processing
1. Upload multiple files simultaneously
2. The system processes files in efficient batches
3. Progress indicators show batch processing status
4. All processed content becomes available for context retrieval

## Customization Options

### System Prompt
1. Click "Edit System Prompt"
2. Modify the AI system instructions
3. Changes affect how the AI interprets requirements

### Scenario Template
1. Click "Edit Scenario Prompt"
2. Customize the scenario generation template
3. Affects the structure and format of generated scenarios

### Context Window
1. Click "Edit Context Window"
2. Choose between 4096 or 8192 tokens
3. Larger windows allow for more context but may be slower

## Working with Generated Scenarios

### Real-time Generation
- Watch as scenarios generate in real-time
- View token counts and generation statistics
- Stop generation at any time if needed

### Inference Statistics
After generation, view:
- Input token count
- Output token count
- Generation time
- Number of retrieved contexts

### Scenario Management
- View scenario history
- Export scenarios to text files
- Clear history when needed
- Regenerate scenarios with same context

## Advanced Features

### Vector Store Management
- Each scenario maintains its own vector store
- Relevant contexts are automatically retrieved
- Historical scenarios remain isolated
- Efficient cleanup of unused vectors

### Image Analysis
When processing images:
1. AI analyzes visual elements
2. Extracts test-relevant information
3. Incorporates visual context into scenarios
4. Maintains traceability to source images

## Best Practices

### For Best Results
1. Provide clear, specific test criteria
2. Upload relevant documentation
3. Include both functional and visual requirements
4. Review and adjust generated scenarios
5. Use appropriate context window size

### Optimizing RAG Performance
1. Upload high-quality documents
2. Ensure images are clear and relevant
3. Use appropriate file formats
4. Balance batch sizes for processing
5. Clean up unused scenarios regularly

## Troubleshooting

### Common Issues
- File Processing Errors:
  - Verify file format support
  - Check file isn't corrupted
  - Ensure file size is reasonable
  
- Generation Issues:
  - Verify LLM server is running
  - Check context window size
  - Review system prompts
  
- Performance Concerns:
  - Monitor batch sizes
  - Clean vector stores regularly
  - Adjust context window if needed

### Error Messages
- Document Processing Errors:
  - Check file permissions
  - Verify file integrity
  - Review supported formats

- Generation Errors:
  - Verify LLM server status
  - Check network connectivity
  - Review token limits

### Support
For technical issues:
1. Check the console for error messages
2. Verify system requirements
3. Review configuration settings
4. Contact support if issues persist

## System Requirements
- Modern web browser
- Stable internet connection
- Access to local LLM server
- Sufficient system resources for processing