"""
Text processing utilities
"""
import re
from typing import Optional, List
import nltk
from nltk.corpus import stopwords

# Ensure NLTK resources are downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def normalize_answer(answer: str) -> str:
    """
    Normalize an answer string for comparison
    
    Args:
        answer: Raw answer string
        
    Returns:
        Normalized answer string
    """
    if not answer:
        return ""
    
    # Convert to string and lowercase
    answer = str(answer).lower().strip()
    
    # Handle percentage answers
    if "%" in answer:
        # Extract the numeric part
        match = re.search(r"(-?\d+\.?\d*)", answer)
        if match:
            value = float(match.group(1))
            # Standardize to one decimal place
            return f"{value:.1f}%"
    
    # Handle currency answers
    if "$" in answer:
        # Remove currency symbol, commas, and text like "million"
        answer = answer.replace("$", "").replace(",", "")
        answer = re.sub(r"\s*(million|billion|thousand|m|b|k)\b", "", answer)
        
        # Extract the numeric part
        match = re.search(r"(-?\d+\.?\d*)", answer)
        if match:
            return match.group(1)
    
    # For other numeric answers, standardize format
    if is_numeric_answer(answer):
        match = re.search(r"(-?\d+\.?\d*)", answer)
        if match:
            value = float(match.group(1))
            # If it's likely a percentage without % symbol
            if 0 <= value <= 100 and ("percent" in answer or "percentage" in answer):
                return f"{value:.1f}%"
            return str(value)
    
    # Remove spaces, punctuation for text answers
    answer = re.sub(r"[^\w\s]", "", answer)
    answer = re.sub(r"\s+", " ", answer).strip()
    
    return answer

def is_numeric_answer(answer: str) -> bool:
    """
    Check if an answer is numeric
    
    Args:
        answer: The answer to check
        
    Returns:
        True if the answer contains a numeric value
    """
    if not answer:
        return False
        
    # Look for numeric pattern
    return bool(re.search(r"(-?\d+\.?\d*)", answer))

def extract_numeric_value(text: str) -> Optional[float]:
    """
    Extract a numeric value from text
    
    Args:
        text: Text containing a numeric value
        
    Returns:
        Extracted numeric value as float, or None if not found
    """
    if not text:
        return None
        
    # Find numeric pattern
    match = re.search(r"(-?\d+\.?\d*)", text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None

def are_numerically_close(answer1: str, answer2: str, tolerance: float = 0.01) -> bool:
    """
    Check if two numeric answers are close enough
    
    Args:
        answer1: First answer
        answer2: Second answer
        tolerance: Relative tolerance for comparison
        
    Returns:
        True if answers are numerically close
    """
    try:
        # Extract numeric values
        val1 = extract_numeric_value(answer1)
        val2 = extract_numeric_value(answer2)
        
        if val1 is None or val2 is None:
            return False
            
        # Check for percentage format consistency
        has_percent1 = "%" in answer1
        has_percent2 = "%" in answer2
        
        # If one has % and the other doesn't, check if they're the same value
        # (e.g., "14.1%" vs "0.141")
        if has_percent1 and not has_percent2:
            if abs(val1 - val2 * 100) < tolerance * abs(val1):
                return True
        elif has_percent2 and not has_percent1:
            if abs(val1 * 100 - val2) < tolerance * abs(val2):
                return True
        
        # Check if values are close
        if abs(val1) < 1e-10 and abs(val2) < 1e-10:
            return True
            
        relative_diff = abs(val1 - val2) / max(abs(val1), abs(val2))
        return relative_diff <= tolerance
    except (ValueError, TypeError):
        return False

def extract_keywords(text: str) -> List[str]:
    """
    Basic keyword extraction
    
    Args:
        text: Input text
        
    Returns:
        List of keywords
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Split into words
    words = text.split()
    
    # Stop words
    stop_words = set(stopwords.words('english'))
    
    # Keep words that aren't stop words and are at least 3 characters long
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Extract years (these are important in financial documents)
    years = re.findall(r'\b(19|20)\d{2}\b', text)
    
    # Add years to keywords and remove duplicates
    return list(set(keywords + years))

def format_table_as_string(table: List[List[str]]) -> str:
    """
    Format a table as a string for LLM input
    
    Args:
        table: Table data as a list of rows
        
    Returns:
        Formatted table string
    """
    result = ""
    for i, row in enumerate(table):
        row_str = "| " + " | ".join(str(cell) for cell in row) + " |"
        result += row_str + "\n"
        
        # Add separator after header row
        if i == 0:
            separator = "| " + " | ".join("---" for _ in row) + " |"
            result += separator + "\n"
    
    return result