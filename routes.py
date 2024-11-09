"""
Route handlers for the test scenario generator application.
"""

import os
import re
from flask import render_template, request, jsonify, Response, stream_with_context
from models import db, TestScenario
from file_processor import process_file
from scenario_generator import (
    generate_scenario_stream,
    update_system_prompt,
    update_context_window,
    update_scenario_prompt
)
from config import Config, logger

def init_routes(app):
    """Initialize all route handlers for the application."""
    
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

    @app.route('/upload', methods=['POST'])
    def upload_file():
        """Handle file uploads and processing."""
        try:
            logger.info("Processing file upload")
            if 'files' not in request.files:
                return jsonify({'error': 'No file part'})
            
            files = request.files.getlist('files')
            if not files or files[0].filename == '':
                return jsonify({'error': 'No selected file'})
            
            results = [process_file(file, app) for file in files]
            return jsonify({'results': results})
        except Exception as e:
            logger.error(f"Error in upload_file: {str(e)}")
            return jsonify({'error': 'File upload failed'}), 500

    @app.route('/generate', methods=['POST'])
    def generate():
        """Generate a test scenario based on provided criteria."""
        try:
            logger.info("Generating test scenario")
            data = request.json
            name = data.get('name')
            criteria = data.get('criteria')
            is_regenerate = data.get('is_regenerate', False)

            if is_regenerate:
                name = re.sub(r'\s*\(Regenerated\)*$', '', name)
                name = f"{name} (Regenerated)"

            def generate_stream():
                scenario = ""
                statistics = ""
                for chunk in generate_scenario_stream(criteria):
                    if chunk.startswith("\n\nInference Statistics:"):
                        statistics = chunk.split("\n\nInference Statistics:\n")[1]
                    else:
                        scenario += chunk
                    yield chunk
                
                uploaded_files = ", ".join(request.json.get('uploaded_files', []))
                new_scenario = TestScenario(
                    name=name,
                    criteria=criteria,
                    scenario=scenario,
                    statistics=statistics,
                    uploaded_files=uploaded_files
                )
                db.session.add(new_scenario)
                db.session.commit()

            return Response(stream_with_context(generate_stream()),
                          content_type='text/plain')
        except Exception as e:
            logger.error(f"Error in generate: {str(e)}")
            return "Error generating scenario", 500

    @app.route('/scenarios', methods=['GET'])
    def get_scenarios():
        """Retrieve all stored test scenarios."""
        if db.engine.has_table('test_scenario'):
            scenarios = TestScenario.query.all()
            return jsonify([{
                'id': s.id,
                'name': s.name,
                'criteria': s.criteria,
                'scenario': s.scenario,
                'statistics': s.statistics,
                'uploaded_files': s.uploaded_files
            } for s in scenarios])
        return jsonify([])

    @app.route('/get_system_prompt', methods=['GET'])
    def get_system_prompt():
        """Get the current system prompt."""
        return jsonify({'prompt': Config.SYSTEM_PROMPT})

    @app.route('/set_system_prompt', methods=['POST'])
    def set_system_prompt():
        """Update the system prompt."""
        data = request.json
        update_system_prompt(data.get('prompt'))
        return jsonify({'success': True})

    @app.route('/get_context_window', methods=['GET'])
    def get_context_window():
        """Get the current context window size."""
        return jsonify({'size': Config.CONTEXT_WINDOW_SIZE})

    @app.route('/set_context_window', methods=['POST'])
    def set_context_window():
        """Update the context window size."""
        data = request.json
        size = data.get('size')
        success = update_context_window(size)
        if success:
            return jsonify({'success': True})
        return jsonify({
            'success': False,
            'error': 'Invalid context window size'
        })

    @app.route('/get_scenario_prompt', methods=['GET'])
    def get_scenario_prompt():
        """Get the current scenario prompt."""
        return jsonify({'prompt': Config.SCENARIO_PROMPT})

    @app.route('/set_scenario_prompt', methods=['POST'])
    def set_scenario_prompt():
        """Update the scenario prompt."""
        data = request.json
        update_scenario_prompt(data.get('prompt'))
        return jsonify({'success': True})

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
