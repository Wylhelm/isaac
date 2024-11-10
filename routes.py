"""
Route handlers for the test scenario generator application.
"""

import os
from flask import render_template, request, jsonify, Response, stream_with_context
from models import db, TestScenario, Document
from file_processor import process_file, cleanup_old_files
from rag_components import EnhancedScenarioGenerator, VectorStoreManager
from config import Config, logger
import numpy as np
from datetime import datetime

def init_routes(app):
    """Initialize all route handlers for the application."""
    
    @app.route('/')
    def index():
        """Render the main application page."""
        try:
            logger.info("Rendering index.html")
            return render_template('index.html')
        except Exception as e:
            logger.error(f"Error rendering index.html: {str(e)}", exc_info=True)
            return f"Error rendering index.html: {str(e)}", 500

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
            
            # Get scenario_id if provided
            scenario_id = request.form.get('scenario_id')
            if scenario_id:
                scenario_id = int(scenario_id)
            
            results = []
            for file in files:
                result = process_file(file, app, scenario_id)
                
                # Associate document with scenario if scenario_id provided
                if scenario_id and 'document_id' in result and not 'error' in result:
                    scenario = TestScenario.query.get(scenario_id)
                    document = Document.query.get(result['document_id'])
                    if scenario and document:
                        scenario.documents.append(document)
                        db.session.commit()
                
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
            
            # Create new scenario
            scenario = TestScenario(
                name=name,
                criteria=criteria,
                scenario="",  # Will be populated during generation
                statistics=""
            )
            db.session.add(scenario)
            db.session.flush()  # Get scenario ID without committing
            
            # Associate any uploaded documents with the scenario
            document_ids = data.get('document_ids', [])
            if document_ids:
                documents = Document.query.filter(Document.id.in_(document_ids)).all()
                scenario.documents.extend(documents)
            
            # Initialize scenario-specific generator
            scenario_generator = EnhancedScenarioGenerator(scenario.id)
            
            scenario_text = ""
            statistics = ""
            
            def generate_stream():
                nonlocal scenario_text, statistics
                
                try:
                    # Generate scenario using RAG
                    for chunk in scenario_generator.generate_scenario(criteria):
                        if chunk.startswith("\n\nInference Statistics:"):
                            statistics = chunk.split("\n\nInference Statistics:\n")[1]
                        else:
                            scenario_text += chunk
                        yield chunk
                    
                    # After generation is complete, save the scenario
                    if scenario_text.strip():
                        scenario.scenario = scenario_text
                        scenario.statistics = statistics
                        db.session.commit()
                        logger.info(f"Successfully saved scenario with ID: {scenario.id}")
                except Exception as e:
                    logger.error(f"Error during scenario generation: {str(e)}")
                    db.session.rollback()
                    yield f"\n\nError during generation: {str(e)}"
            
            return Response(stream_with_context(generate_stream()),
                          content_type='text/plain')
            
        except Exception as e:
            logger.error(f"Error in generate: {str(e)}")
            return "Error generating scenario", 500

    @app.route('/scenarios', methods=['GET'])
    def get_scenarios():
        """Retrieve all stored test scenarios."""
        try:
            logger.info("Retrieving scenarios from database")
            scenarios = TestScenario.query.order_by(TestScenario.created_at.desc()).all()
            
            result = [{
                'id': s.id,
                'name': s.name,
                'criteria': s.criteria,
                'scenario': s.scenario,
                'statistics': s.statistics,
                'created_at': s.created_at.isoformat() if s.created_at else None,
                'documents': [{
                    'id': doc.id,
                    'filename': doc.filename,
                    'file_type': doc.file_type,
                    'file_path': doc.file_path,
                    'has_image_analysis': bool(doc.image_analysis),
                    'upload_date': doc.upload_date.isoformat() if doc.upload_date else None
                } for doc in s.documents]
            } for s in scenarios]
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error retrieving scenarios: {str(e)}")
            return jsonify({'error': 'Failed to retrieve scenarios'}), 500

    @app.route('/scenario/<int:scenario_id>', methods=['GET'])
    def get_scenario(scenario_id):
        """Retrieve a specific scenario with its associated documents."""
        try:
            scenario = TestScenario.query.get_or_404(scenario_id)
            
            result = {
                'id': scenario.id,
                'name': scenario.name,
                'criteria': scenario.criteria,
                'scenario': scenario.scenario,
                'statistics': scenario.statistics,
                'created_at': scenario.created_at.isoformat() if scenario.created_at else None,
                'documents': [{
                    'id': doc.id,
                    'filename': doc.filename,
                    'file_type': doc.file_type,
                    'file_path': doc.file_path,
                    'has_image_analysis': bool(doc.image_analysis),
                    'upload_date': doc.upload_date.isoformat() if doc.upload_date else None
                } for doc in scenario.documents]
            }
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error retrieving scenario {scenario_id}: {str(e)}")
            return jsonify({'error': f'Failed to retrieve scenario {scenario_id}'}), 500

    @app.route('/clear_history', methods=['POST'])
    def clear_history():
        """Clear all stored test scenarios and their associated data."""
        try:
            # Get all scenarios
            scenarios = TestScenario.query.all()
            
            # Clean up vector stores for each scenario
            for scenario in scenarios:
                VectorStoreManager.cleanup_scenario_vectors(scenario.id)
            
            # Delete all scenarios (will cascade to associated data)
            TestScenario.query.delete()
            
            # Clean up old files
            cleanup_old_files(app)
            
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
