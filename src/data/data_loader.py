"""
Data loading utilities
"""
import os
import json
from typing import List, Dict, Any, Optional
from utils.logging_utils import setup_logging

# Setup logger
logger = setup_logging("DataLoader")

def find_dataset_file() -> Optional[str]:
    """
    Find the dataset file in standard locations
    
    Returns:
        Path to dataset file if found, None otherwise
    """
    standard_paths = [
        "train.json", 
        "data/train.json", 
        "../data/train.json",
        "datasets/train.json",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/train.json")
    ]
    
    for path in standard_paths:
        if os.path.exists(path):
            logger.info(f"Found dataset at {path}")
            return path
    
    return None

def load_dataset(file_path: str) -> List[Dict[str, Any]]:
    """
    Load a dataset from JSON file
    
    Args:
        file_path: Path to the dataset file
        
    Returns:
        Loaded dataset as a list of examples
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} examples from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading dataset {file_path}: {e}")
        return []

def save_results(data: Dict[str, Any], filename: str, output_dir: str) -> str:
    """
    Save results to a JSON file
    
    Args:
        data: The data to save
        filename: Base filename
        output_dir: Output directory
        
    Returns:
        Path to the saved file
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create full file path
    file_path = os.path.join(output_dir, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved results to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving results to {file_path}: {e}")
        return ""