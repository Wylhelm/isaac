"""
Main application module for the test scenario generator.
Initializes and configures the Flask application.
"""

import os
import sqlite3
from flask import Flask
from models import db, init_db
from routes import init_routes
from config import Config, logger

def verify_db_access():
    """Verify database file is accessible and SQLite can open it."""
    try:
        # Try to connect to the database
        conn = sqlite3.connect(Config.DB_PATH)
        # Test creating a table to verify write access
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS test_table
                         (id INTEGER PRIMARY KEY)''')
        cursor.execute('DROP TABLE test_table')
        conn.close()
        logger.info(f"Successfully verified database access at {Config.DB_PATH}")
        return True
    except sqlite3.Error as e:
        logger.error(f"SQLite error verifying database access: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error verifying database access: {str(e)}")
        return False

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    try:
        # Create Flask app with explicit instance path
        instance_path = os.path.abspath(Config.INSTANCE_PATH)
        app = Flask(__name__, 
                    instance_path=instance_path,
                    instance_relative_config=True,
                    static_folder='static',
                    static_url_path='/static')
        
        logger.info(f"Created Flask app with instance path: {instance_path}")
        
        # Verify database access
        if not verify_db_access():
            raise Exception("Unable to access database file")
        
        # Configure the application
        app.config.from_object(Config)
        logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Initialize extensions
        db.init_app(app)
        logger.info("Initialized database extension")
        
        # Initialize database and create tables
        with app.app_context():
            db.create_all()
            logger.info("Created all database tables")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Existing tables in database: {tables}")
        
        # Register routes
        init_routes(app)
        logger.info("Registered routes")
        
        return app
        
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        logger.info("Starting the Flask application")
        
        # Create required directories
        for directory in [Config.UPLOAD_FOLDER, Config.VECTOR_DB_PATH, Config.INSTANCE_PATH]:
            os.makedirs(directory, mode=0o755, exist_ok=True)
            logger.info(f"Ensured directory exists with proper permissions: {directory}")
        
        # Create the application
        app = create_app()
        
        # Run the application
        app.run(debug=True)
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    finally:
        logger.info("Flask application has stopped")
