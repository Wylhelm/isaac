"""
Database models for the test scenario generator application.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TestScenario(db.Model):
    """
    TestScenario model representing a generated test scenario.
    
    Attributes:
        id (int): Primary key
        name (str): Name of the test scenario
        criteria (str): Input criteria used to generate the scenario
        scenario (str): Generated scenario content
        statistics (str): Generation statistics
        uploaded_files (str): List of files used in generation
    """
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    criteria = db.Column(db.Text, nullable=False)
    scenario = db.Column(db.Text, nullable=False)
    statistics = db.Column(db.Text)
    uploaded_files = db.Column(db.Text)

def init_db(app):
    """Initialize the database with the Flask application context."""
    with app.app_context():
        db.create_all()
