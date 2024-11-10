"""
Main application module for the test scenario generator.
"""

import os
from dotenv import load_dotenv

# Load environment variables before any other imports
load_dotenv()

from flask import Flask
from flask_migrate import Migrate
from models import db, init_db
from routes import init_routes
from config import Config, logger
import atexit

def create_app():
    """Create and configure the Flask application."""
    try:
        # Initialize Flask app
        app = Flask(__name__)
        
        # Configure app
        instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        app.config['INSTANCE_PATH'] = instance_path
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "isaac.db")}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        
        # Ensure required directories exist
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        vector_store_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vector_store')
        os.makedirs(vector_store_path, exist_ok=True)
        Config.VECTOR_DB_PATH = vector_store_path
        
        # Initialize database
        db.init_app(app)
        
        # Initialize migrations
        migrate = Migrate(app, db)
        
        # Initialize routes
        init_routes(app)
        
        # Initialize database tables
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
        
        # Register cleanup function
        def cleanup():
            """Cleanup function to run on application shutdown."""
            try:
                from file_processor import cleanup_old_files
                with app.app_context():
                    cleanup_old_files(app)
                logger.info("Cleanup completed successfully")
            except Exception as e:
                logger.error(f"Error during cleanup: {str(e)}")
        
        atexit.register(cleanup)
        
        logger.info("Application initialized successfully")
        return app
        
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
