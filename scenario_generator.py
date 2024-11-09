"""
Scenario generation module for creating test scenarios.
"""

import time
import json
import requests
from config import Config, logger

def generate_scenario_stream(criteria):
    """
    Generate a test scenario using streaming response.
    
    Args:
        criteria (str): The criteria for generating the test scenario
    
    Yields:
        str: Chunks of generated scenario content and statistics
    """
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": Config.SYSTEM_PROMPT},
            {"role": "user", "content": Config.SCENARIO_PROMPT.format(criteria=criteria)}
        ],
        "max_tokens": Config.CONTEXT_WINDOW_SIZE,
        "stream": True
    }
    
    start_time = time.time()
    input_tokens = len(Config.SYSTEM_PROMPT.split()) + len(Config.SCENARIO_PROMPT.format(criteria=criteria).split())
    output_tokens = 0
    scenario = ""
    
    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    try:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            json_str = line_text[6:]  # Remove 'data: ' prefix
                            json_object = json.loads(json_str)
                            if 'choices' in json_object and len(json_object['choices']) > 0:
                                delta = json_object['choices'][0]['delta']
                                if 'content' in delta:
                                    content = delta['content']
                                    output_tokens += len(content.split())
                                    scenario += content
                                    yield content
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON: {line_text}")
                    except Exception as e:
                        logger.error(f"Error processing line: {str(e)}")
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Generate statistics
            statistics = (
                f"Input Tokens: {input_tokens}\n"
                f"Output Tokens: {output_tokens}\n"
                f"Generation Time: {generation_time:.2f} seconds"
            )
            yield f"\n\nInference Statistics:\n{statistics}"
        else:
            error_msg = f"Error generating scenario: HTTP {response.status_code}"
            logger.error(error_msg)
            yield error_msg
    except Exception as e:
        error_msg = f"Error in generate_scenario_stream: {str(e)}"
        logger.error(error_msg)
        yield error_msg

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
