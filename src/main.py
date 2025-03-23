"""
Main entry point for the Financial QA system
"""
import os
import time
import argparse
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

from config import QA_HISTORY_DIR
from utils.logging_utils import setup_logging
from data.data_loader import load_dataset, find_dataset_file
from models.qa_system import FinancialQASystem
from models.document_retrieval import enhanced_document_retrieval
from evaluate import run_evaluation

# Setup logger
logger = setup_logging("Main")

def run_qa_mode(system: FinancialQASystem, knowledge_base: List[Dict[str, Any]]):
    """
    Run interactive QA mode
    
    Args:
        system: FinancialQASystem instance
        knowledge_base: List of documents for retrieval
    """
    from data.data_loader import save_results
    
    logger.info("Starting QA mode")
    print("\n===== Financial QA Mode =====")
    print("Ask any financial question. Type 'exit' to quit.")
    
    # Initialize session history
    qa_history = []
    
    while True:
        # Get question from user
        question = input("\nYour question: ")
        if question.lower() in ["exit", "quit", "q"]:
            break
        
        # Search for relevant documents
        print("\nSearching knowledge base...")
        relevant_docs = enhanced_document_retrieval(question, knowledge_base, system.client, top_k=1)
        
        if not relevant_docs:
            print("I couldn't find relevant information to answer this question.")
            continue
        
        # Use the most relevant document to answer
        best_doc = relevant_docs[0]
        
        print("Thinking...")
        
        # Get the answer
        start_time = time.time()
        answer_result = system.answer_question(best_doc, question)
        elapsed_time = time.time() - start_time
        
        # Save to qa history
        qa_history.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer_result["answer"],
            "document_id": best_doc.get("id", ""),
            "document_filename": best_doc.get("filename", ""),
            "processing_time": elapsed_time
        })
        
        # Display answer
        print("\n===== Answer =====")
        if answer_result["answer"]:
            print(answer_result["answer"])
        else:
            # Debugging: If the answer is empty, try to extract from full response
            print("Could not extract a clear answer. Here is the complete response:")
            print("-" * 50)
            print(answer_result["full_response"][:500] + "..." if len(answer_result["full_response"]) > 500 else answer_result["full_response"])
            print("-" * 50)
        
        print(f"\nSource: {answer_result['source']}")
        print(f"Processing time: {elapsed_time:.2f} seconds")
        
        # Display token usage for this request
        print(f"Token usage: {system.token_usage['prompt_tokens']} prompt, {system.token_usage['completion_tokens']} completion")
        
        # Optionally show reasoning if requested
        show_reasoning = input("\nWould you like to see the reasoning? (y/n): ")
        if show_reasoning.lower() == "y":
            print("\n===== Reasoning =====")
            if isinstance(answer_result["reasoning"], list):
                for step in answer_result["reasoning"]:
                    print(f"- {step}")
            else:
                print(answer_result["reasoning"])
    
    # After exiting, save the QA history
    if qa_history:
        # Create a timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        qa_history_file = os.path.join(QA_HISTORY_DIR, f"qa_history_{timestamp}.json")
        
        # Save history to file
        save_results(qa_history, f"qa_history_{timestamp}.json", QA_HISTORY_DIR)
        
        print(f"\nQA session history saved to {qa_history_file}")
    
    # Display token usage and cost
    print(system.get_token_usage_report())

def main():
    """Main function"""
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Financial QA System")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--model", default="gpt-4o", help="Model to use")
    parser.add_argument("--data", help="Path to dataset file")
    parser.add_argument("--mode", choices=["qa", "evaluate"], default="qa", 
                        help="Operation mode: qa (interactive) or evaluate")
    parser.add_argument("--limit", type=int, help="Number of examples for evaluation")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = input("Please enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = api_key
    
    # Find dataset file
    dataset_path = args.data
    if not dataset_path:
        dataset_path = find_dataset_file()
        if not dataset_path:
            print("Error: Dataset file not found. Please specify with --data")
            return
    
    # Load dataset
    dataset = load_dataset(dataset_path)
    if not dataset:
        print(f"Error: Could not load dataset from {dataset_path}")
        return
    
    print(f"Loaded {len(dataset)} examples from {dataset_path}")
    
    # Initialize QA system
    system = FinancialQASystem(api_key=api_key, model=args.model)
    
    # Run in selected mode
    if args.mode == "qa":
        run_qa_mode(system, dataset)
    elif args.mode == "evaluate":
        print(f"Running evaluation on {args.limit if args.limit else 'all'} examples...")
        run_evaluation(system, dataset, limit=args.limit)
    else:
        print(f"Unknown mode: {args.mode}")

if __name__ == "__main__":
    main()