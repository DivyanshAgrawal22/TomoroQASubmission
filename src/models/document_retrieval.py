"""
Document retrieval functionality
"""
from typing import List, Dict, Any
from openai import OpenAI
from utils.logging_utils import setup_logging
from config import EXTRACTION_MODEL

# Setup logger
logger = setup_logging("DocumentRetrieval")

def extract_keywords_with_llm(question: str, client: OpenAI) -> List[str]:
    """
    Extract keywords from a question using an LLM
    
    Args:
        question: The question to analyze
        client: OpenAI client
        
    Returns:
        List of extracted keywords
    """
    from utils.text_processing import extract_keywords
    
    prompt = f"""
        Extract the most important search keywords from this financial question:
        
        "{question}"
        
        Return ONLY a comma-separated list of 3-7 keywords, with no numbering, explanation, or additional text.
        Focus on specific terms, years, financial metrics, and entities that would be useful for document retrieval.
        Remove general words like 'what', 'how', etc.
    """
    
    try:
        response = client.chat.completions.create(
            model=EXTRACTION_MODEL,
            messages=[
                {"role": "system", "content": "You are a keyword extraction expert that identifies the most relevant search terms."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=50
        )
        
        keywords_text = response.choices[0].message.content.strip()
        # Split by commas and clean up
        keywords = [k.strip().lower() for k in keywords_text.split(',') if k.strip()]
        
        # Ensure we have some keywords
        if not keywords:
            # Fall back to basic extraction
            return extract_keywords(question)
            
        return keywords
    
    except Exception as e:
        logger.error(f"Error in LLM keyword extraction: {e}")
        # Fall back to basic extraction
        return extract_keywords(question)

def enhanced_document_retrieval(question: str, documents: List[Dict[str, Any]], client: OpenAI, top_k: int = 1) -> List[Dict[str, Any]]:
    """
    Enhanced document retrieval using LLM-extracted keywords
    
    Args:
        question: The question
        documents: List of documents
        client: OpenAI client
        top_k: Number of documents to return
        
    Returns:
        List of relevant documents
    """
    # Extract keywords from the question using LLM
    keywords = extract_keywords_with_llm(question, client)
    logger.info(f"Extracted keywords with LLM: {', '.join(keywords)}")
    
    # Use the document retrieval function with extracted keywords
    from data.document_utils import compute_document_relevance
    
    # Score documents by relevance
    scored_docs = []
    for doc in documents:
        score = compute_document_relevance(keywords, doc)
        scored_docs.append((score, doc))
    
    # Sort by relevance score (descending)
    scored_docs.sort(reverse=True, key=lambda x: x[0])
    
    # Return top k documents
    return [doc for _, doc in scored_docs[:top_k]]