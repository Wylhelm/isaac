"""
Main application module for the test scenario generator.
Initializes and configures the Flask application.
"""

from flask import Flask
from models import db, init_db
from routes import init_routes
from config import Config, logger

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    # Configure the application
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize database
    init_db(app)
    
    # Register routes
    init_routes(app)
    
    return app

if __name__ == '__main__':
    logger.info("Starting the Flask application")
    app = create_app()
    app.run(debug=True)
    logger.info("Flask application has stopped")
