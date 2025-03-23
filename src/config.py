"""
Configuration and settings for the Financial QA system
"""
import os
from datetime import datetime

# Basic configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Create subfolders for different output types
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
LOGS_DIR = os.path.join(OUTPUT_DIR, "logs")
QA_HISTORY_DIR = os.path.join(OUTPUT_DIR, "qa_history")

# Create all output directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(QA_HISTORY_DIR, exist_ok=True)

# Timestamp format for logs and output files
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
CURRENT_TIMESTAMP = datetime.now().strftime(TIMESTAMP_FORMAT)

# Log file path
LOG_FILE = os.path.join(LOGS_DIR, f"finqa_log_{CURRENT_TIMESTAMP}.log")

# OpenAI API configuration
DEFAULT_MODEL = "gpt-4o"
EXTRACTION_MODEL = "gpt-3.5-turbo"  # Use cheaper model for extraction tasks

# Cost per 1000 tokens (for cost estimation)
COST_PER_1K = {
    "gpt-4o": {"prompt": 0.0025, "completion": 0.01},
    "o1": {"prompt": 0.015, "completion": 0.06},
    "gpt-4.5-preview": {"prompt": 0.075, "completion": 0.15},
    "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015}
}

# Evaluation configuration
DEFAULT_EVAL_SAMPLE_SIZE = 5
NUMERIC_COMPARISON_TOLERANCE = 0.01  # 1% tolerance for numeric comparison

# Prompt configuration
SYSTEM_PROMPT = """
You are a financial analyst expert at answering questions about financial documents.
Analyze the provided document carefully and answer the question with precision.
Show your reasoning step by step, explaining how you extracted the relevant information and performed any calculations.
Be especially precise with numerical answers and follow proper financial formatting conventions.
Always provide your final answer on a new line starting with "Final Answer:", making sure percentages have exactly one decimal place.
"""

# Question categorization
QUESTION_TYPES = {
    "percentage": ["percent", "percentage"],
    "change": ["increase", "decrease", "change", "growth", "difference"],
    "factual": ["what is", "what was", "what are", "what were"],
    "quantity": ["how much", "how many"],
    "explanation": ["why", "how", "explain"],
    "comparison": ["compare", "difference between", "versus", "vs"]
}