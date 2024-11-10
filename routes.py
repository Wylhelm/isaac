"""
Route handlers for the test scenario generator application.
"""

import os
from flask import render_template, request, jsonify, Response, stream_with_context
from models import db, TestScenario
from file_processor import process_file
from rag_components import EnhancedScenarioGenerator, VectorStoreManager
from config import Config, logger
import numpy as np

def init_routes(app):
    """Initialize all route handlers for the application."""
    
    # Initialize vector store
    vector_store = VectorStoreManager()
    scenario_generator = EnhancedScenarioGenerator()
    
    @app.route('/')
    def index():
        """Render the main application page."""
        try:
            logger.info("Rendering index.html")
            return render_template('index.html',
                                scenario_name='',
                                scenario_description='',
                                scenario_statistics='')
        except Exception as e:
            logger.error(f"Error rendering index.html: {str(e)}", exc_info=True)
            return f"Error rendering index.html: {str(e)}", 500

    @app.route('/get_system_prompt', methods=['GET'])
    def get_system_prompt():
        """Retrieve the system prompt."""
        try:
            return jsonify({'system_prompt': Config.SYSTEM_PROMPT})
        except Exception as e:
            logger.error(f"Error retrieving system prompt: {str(e)}")
            return jsonify({'error': 'Failed to retrieve system prompt'}), 500

    @app.route('/set_system_prompt', methods=['POST'])
    def set_system_prompt():
        """Update the system prompt."""
        try:
            data = request.json
            Config.SYSTEM_PROMPT = data.get('prompt')
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error updating system prompt: {str(e)}")
            return jsonify({'error': 'Failed to update system prompt'}), 500

    @app.route('/get_scenario_prompt', methods=['GET'])
    def get_scenario_prompt():
        """Retrieve the scenario prompt template."""
        try:
            return jsonify({'scenario_prompt': Config.SCENARIO_PROMPT})
        except Exception as e:
            logger.error(f"Error retrieving scenario prompt: {str(e)}")
            return jsonify({'error': 'Failed to retrieve scenario prompt'}), 500

    @app.route('/set_scenario_prompt', methods=['POST'])
    def set_scenario_prompt():
        """Update the scenario prompt template."""
        try:
            data = request.json
            Config.SCENARIO_PROMPT = data.get('prompt')
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error updating scenario prompt: {str(e)}")
            return jsonify({'error': 'Failed to update scenario prompt'}), 500

    @app.route('/get_context_window', methods=['GET'])
    def get_context_window():
        """Retrieve the context window size."""
        try:
            return jsonify({'context_window': Config.CONTEXT_WINDOW_SIZE})
        except Exception as e:
            logger.error(f"Error retrieving context window: {str(e)}")
            return jsonify({'error': 'Failed to retrieve context window'}), 500

    @app.route('/set_context_window', methods=['POST'])
    def set_context_window():
        """Update the context window size."""
        try:
            data = request.json
            Config.CONTEXT_WINDOW_SIZE = int(data.get('size'))
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error updating context window: {str(e)}")
            return jsonify({'error': 'Failed to update context window'}), 500

    @app.route('/upload', methods=['POST'])
    def upload_file():
        """Handle file uploads and RAG processing."""
        try:
            logger.info("Processing file upload with RAG")
            if 'files' not in request.files:
                return jsonify({'error': 'No file part'})
            
            files = request.files.getlist('files')
            if not files or files[0].filename == '':
                return jsonify({'error': 'No selected file'})
            
            results = []
            for file in files:
                result = process_file(file, app)
                if 'error' not in result:
                    logger.info(f"Successfully processed {result['filename']} with {result['chunks_processed']} chunks")
                results.append(result)
            
            return jsonify({'results': results})
        except Exception as e:
            logger.error(f"Error in upload_file: {str(e)}")
            return jsonify({'error': 'File upload failed'}), 500

    @app.route('/generate', methods=['POST'])
    def generate():
        """Generate a test scenario using RAG."""
        try:
            logger.info("Generating test scenario with RAG")
            data = request.json
            name = data.get('name', '')
            criteria = data.get('criteria', '')
            
            scenario_text = ""
            statistics = ""
            
            def generate_stream():
                nonlocal scenario_text, statistics
                
                # Generate scenario using RAG
                for chunk in scenario_generator.generate_scenario(criteria):
                    if chunk.startswith("\n\nInference Statistics:"):
                        statistics = chunk.split("\n\nInference Statistics:\n")[1]
                    else:
                        scenario_text += chunk
                    yield chunk
            
            response = Response(stream_with_context(generate_stream()),
                              content_type='text/plain')
            
            # After generation is complete, store the scenario
            scenario = TestScenario(
                name=name,
                criteria=criteria,
                scenario=scenario_text,
                statistics=statistics,
                uploaded_files=", ".join(data.get('uploaded_files', []))
            )
            
            # Generate and store embedding for the scenario
            embedding = vector_store.embeddings.embed_query(scenario_text)
            if isinstance(embedding, list):
                embedding = np.array(embedding)
            scenario.set_vector_embedding(embedding)
            
            db.session.add(scenario)
            db.session.commit()
            
            return response
            
        except Exception as e:
            logger.error(f"Error in generate: {str(e)}")
            return "Error generating scenario", 500

    @app.route('/scenarios', methods=['GET'])
    def get_scenarios():
        """Retrieve all stored test scenarios."""
        try:
            if db.engine.has_table('test_scenario'):
                scenarios = TestScenario.query.all()
                return jsonify([{
                    'id': s.id,
                    'name': s.name,
                    'criteria': s.criteria,
                    'scenario': s.scenario if s.scenario else 'Scenario content is not available.',
                    'statistics': s.statistics,
                    'uploaded_files': s.uploaded_files
                } for s in scenarios])
            return jsonify([])
        except Exception as e:
            logger.error(f"Error retrieving scenarios: {str(e)}")
            return jsonify({'error': 'Failed to retrieve scenarios'}), 500

    @app.route('/similar_scenarios', methods=['POST'])
    def find_similar_scenarios():
        """Find similar scenarios using vector similarity search."""
        try:
            data = request.json
            query = data.get('query', '')
            k = data.get('k', 5)  # Number of similar scenarios to return
            
            # Get embedding for query
            query_embedding = vector_store.embeddings.embed_query(query)
            if isinstance(query_embedding, list):
                query_embedding = np.array(query_embedding)
            
            # Get all scenarios with their embeddings
            scenarios = TestScenario.query.all()
            scenario_embeddings = [
                (scenario, scenario.get_vector_embedding())
                for scenario in scenarios
                if scenario.vector_embedding is not None
            ]
            
            # Calculate similarities and sort
            from numpy.linalg import norm
            from numpy import dot
            
            def cosine_similarity(a, b):
                return dot(a, b) / (norm(a) * norm(b))
            
            similarities = [
                (scenario, cosine_similarity(query_embedding, embedding))
                for scenario, embedding in scenario_embeddings
            ]
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Return top k similar scenarios
            return jsonify([{
                'id': s[0].id,
                'name': s[0].name,
                'similarity': float(s[1])
            } for s in similarities[:k]])
            
        except Exception as e:
            logger.error(f"Error finding similar scenarios: {str(e)}")
            return jsonify({'error': 'Failed to find similar scenarios'}), 500

    @app.route('/clear_history', methods=['POST'])
    def clear_history():
        """Clear all stored test scenarios."""
        try:
            TestScenario.query.delete()
            db.session.commit()
            return jsonify({'success': True}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error clearing history: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/debug')
    def debug():
        """Debug endpoint to verify application is running."""
        return "Debug route is working"
