"""
Document handling utilities
"""
from typing import Dict, Any, List
from utils.text_processing import format_table_as_string, extract_keywords

def format_document_context(document: Dict[str, Any]) -> str:
    """
    Format document context for the LLM
    
    Args:
        document: The document data
        
    Returns:
        Formatted context string
    """
    context = ""
    
    # Add document ID for reference
    if document.get('id'):
        context += f"DOCUMENT ID: {document['id']}\n\n"
    elif document.get('filename'):
        context += f"DOCUMENT: {document['filename']}\n\n"
    
    # Add pre-text
    if document.get('pre_text'):
        context += "TEXT BEFORE TABLE:\n"
        context += " ".join(document['pre_text']) + "\n\n"
    
    # Format table
    if document.get('table'):
        context += "TABLE:\n"
        context += format_table_as_string(document['table']) + "\n\n"
    
    # Add post-text
    if document.get('post_text'):
        context += "TEXT AFTER TABLE:\n"
        context += " ".join(document['post_text']) + "\n\n"
    
    return context

def extract_document_source(document: Dict[str, Any]) -> str:
    """
    Extract source information from document
    
    Args:
        document: The document data
        
    Returns:
        Source information string
    """
    if document.get('id'):
        return f"Document ID: {document['id']}"
    elif document.get('filename'):
        return f"Document: {document['filename']}"
    else:
        return "Source: Unknown document"

def compute_document_relevance(keywords: List[str], document: Dict[str, Any]) -> float:
    """
    Compute relevance score for a document based on keywords
    
    Args:
        keywords: List of keywords
        document: Document to score
        
    Returns:
        Relevance score
    """
    score = 0
    
    # Check if the document has a question
    if "qa" in document and "question" in document["qa"]:
        # If document question contains keywords, it's likely relevant
        doc_question = document["qa"]["question"].lower()
        for keyword in keywords:
            if keyword in doc_question:
                score += 10  # High weight for matching question
    
    # Check pre_text and post_text
    text_content = ""
    if "pre_text" in document:
        text_content += " ".join(document["pre_text"]).lower()
    if "post_text" in document:
        text_content += " ".join(document["post_text"]).lower()
    
    for keyword in keywords:
        if keyword in text_content:
            score += 1
    
    # Check table content
    if "table" in document:
        table = document["table"]
        table_text = ""
        for row in table:
            table_text += " ".join(str(cell).lower() for cell in row)
        
        for keyword in keywords:
            if keyword in table_text:
                score += 5  # Higher weight for table content
    
    return score

def find_relevant_documents(
    question: str, 
    documents: List[Dict[str, Any]], 
    top_k: int = 1
) -> List[Dict[str, Any]]:
    """
    Find the most relevant documents for a question using keywords
    
    Args:
        question: The question
        documents: List of documents
        top_k: Number of documents to return
        
    Returns:
        List of relevant documents
    """
    # Extract keywords from the question
    keywords = extract_keywords(question)
    
    # Score documents by relevance
    scored_docs = []
    for doc in documents:
        score = compute_document_relevance(keywords, doc)
        scored_docs.append((score, doc))
    
    # Sort by relevance score (descending)
    scored_docs.sort(reverse=True, key=lambda x: x[0])
    
    # Return top k documents
    return [doc for _, doc in scored_docs[:top_k]]

def categorize_questions(examples: List[Dict[str, Any]], type_keywords: Dict[str, List[str]]) -> Dict[str, int]:
    """
    Categorize and count question types
    
    Args:
        examples: List of example documents
        type_keywords: Dictionary mapping question types to keywords
        
    Returns:
        Dictionary with question type counts
    """
    from collections import Counter
    question_types = Counter()
    
    for example in examples:
        if "qa" in example and "question" in example["qa"]:
            question = example["qa"]["question"].lower()
            
            # Determine question type
            q_type = "other"  # Default type
            for type_name, keywords in type_keywords.items():
                if any(kw in question for kw in keywords):
                    q_type = type_name
                    break
            
            question_types[q_type] += 1
    
    return dict(question_types)