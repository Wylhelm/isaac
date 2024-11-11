"""
Scenario generation module for creating test scenarios.
"""

from config import Config
from rag_components import EnhancedScenarioGenerator

def generate_scenario_stream(criteria):
    """
    Generate a test scenario using streaming response with RAG.
    
    Args:
        criteria (str): The criteria for generating the test scenario
    
    Yields:
        str: Chunks of generated scenario content and statistics
    """
    generator = EnhancedScenarioGenerator()
    yield from generator.generate_scenario_stream(criteria)

def update_system_prompt(prompt):
    """Update the system prompt configuration."""
    Config.SYSTEM_PROMPT = prompt

def update_context_window(size):
    """
    Update the context window size configuration.
    
    Args:
        size (int): New context window size (4096 or 8192)
    
    Returns:
        bool: True if update successful, False otherwise
    """
    if size in [4096, 8192]:
        Config.CONTEXT_WINDOW_SIZE = size
        return True
    return False

def update_scenario_prompt(prompt):
    """Update the scenario prompt configuration."""
    Config.SCENARIO_PROMPT = prompt
