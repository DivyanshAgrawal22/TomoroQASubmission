"""
Evaluation of Financial QA System
"""
import time
import random
from typing import Dict, List, Any, Optional
import argparse
import os

from config import DEFAULT_EVAL_SAMPLE_SIZE
from utils.logging_utils import setup_logging
from data.data_loader import load_dataset, find_dataset_file
from models.qa_system import FinancialQASystem
from evaluation.metrics import evaluate_predictions
from evaluation.reporting import save_evaluation_report, print_evaluation_summary
from data.document_utils import categorize_questions
from config import QUESTION_TYPES

# Setup logger
logger = setup_logging("Evaluation")

def run_evaluation(
    system: FinancialQASystem, 
    eval_data: List[Dict[str, Any]], 
    limit: Optional[int] = None,
    output_report: bool = True
) -> Dict[str, Any]:
    """
    Run evaluation on the given data
    
    Args:
        system: FinancialQASystem instance
        eval_data: List of evaluation examples
        limit: Optional limit on the number of examples to evaluate
        output_report: Whether to generate and save an evaluation report
        
    Returns:
        Evaluation results
    """
    logger.info("Starting evaluation")
    
    # Reset token usage
    system.reset_token_usage()
    
    # Check and filter valid examples
    valid_examples = []
    for example in eval_data:
        if "qa" in example and "question" in example["qa"] and "answer" in example["qa"]:
            valid_examples.append(example)
    
    logger.info(f"Found {len(valid_examples)} valid examples with qa/question/answer out of {len(eval_data)} total")
    
    if not valid_examples:
        logger.warning("No valid examples found for evaluation!")
        return {"error": "No valid examples found"}
    
    # Randomize examples for evaluation
    random.shuffle(valid_examples)
    logger.info("Examples randomized for evaluation")
    
    # Apply limit if specified
    if limit and limit > 0:
        valid_examples = valid_examples[:limit]
        logger.info(f"Limiting evaluation to {limit} examples")
    
    total = len(valid_examples)
    
    # Prepare lists for evaluation
    ground_truths = []
    predictions = []
    questions = []
    processing_times = []
    documents = []
    
    # Track progress
    start_time = time.time()
    for i, example in enumerate(valid_examples):
        document = example
        question = example["qa"]["question"]
        ground_truth = example["qa"]["answer"]
        
        # Print progress
        elapsed = time.time() - start_time
        examples_per_second = (i + 1) / elapsed if elapsed > 0 else 0
        eta = (total - i - 1) / examples_per_second if examples_per_second > 0 else "unknown"
        eta_str = f"{eta:.1f} seconds" if isinstance(eta, float) else eta
        
        logger.info(f"Processing example {i+1}/{total} ({examples_per_second:.2f}/sec, ETA: {eta_str})")
        logger.info(f"Question: {question}")
        
        # Get prediction
        try:
            logger.info(f"Getting answer for: {question}")
            prediction_result = system.answer_question(document, question)
            prediction = prediction_result["answer"]
            
            # Log result
            logger.info(f"  Ground truth: {ground_truth}")
            logger.info(f"  Prediction: {prediction}")
            
            # Add to lists
            ground_truths.append(ground_truth)
            predictions.append(prediction)
            questions.append(question)
            processing_times.append(prediction_result.get("processing_time", 0))
            documents.append(document)
            
        except Exception as e:
            logger.error(f"Error processing example {i+1}: {e}")
            continue
    
    # Evaluate predictions
    logger.info("Evaluating predictions")
    evaluation = evaluate_predictions(
        ground_truths=ground_truths,
        predictions=predictions,
        questions=questions,
        processing_times=processing_times
    )
    
    # Add question types analysis
    question_types = categorize_questions(valid_examples, QUESTION_TYPES)
    
    type_stats = {}
    for q_type, count in question_types.items():
        type_stats[q_type] = {
            "count": count,
            "correct": 0,
            "incorrect": 0,
            "accuracy": 0
        }
    
    # Count correct/incorrect per question type
    for i, question in enumerate(questions):
        if i < len(evaluation["details"]):
            q_type = "other"
            for type_name, keywords in QUESTION_TYPES.items():
                if any(kw in question.lower() for kw in keywords):
                    q_type = type_name
                    break
            
            if evaluation["details"][i].get("is_correct", False):
                type_stats[q_type]["correct"] += 1
            else:
                type_stats[q_type]["incorrect"] += 1
    
    # Calculate accuracy per question type
    for q_type, stats in type_stats.items():
        if stats["count"] > 0:
            stats["accuracy"] = stats["correct"] / stats["count"] * 100
    
    # Add token usage and cost
    cost_per_1k = {
        "gpt-4o": {"prompt": 0.0025, "completion": 0.01}
    }.get(system.model, {"prompt": 0.0025, "completion": 0.01})
    
    prompt_cost = (system.token_usage["prompt_tokens"] / 1000) * cost_per_1k["prompt"]
    completion_cost = (system.token_usage["completion_tokens"] / 1000) * cost_per_1k["completion"]
    total_cost = prompt_cost + completion_cost
    
    # Combine all results
    evaluation.update({
        "question_types": type_stats,
        "token_usage": system.token_usage,
        "cost": {
            "prompt_cost": prompt_cost,
            "completion_cost": completion_cost,
            "total_cost": total_cost,
            "currency": "USD"
        },
        "model": system.model,
        "start_time": start_time,
        "end_time": time.time(),
        "duration": time.time() - start_time
    })
    
    # Save evaluation report
    if output_report:
        md_file, json_file = save_evaluation_report(evaluation)
        logger.info(f"Saved evaluation report to {md_file}")
        logger.info(f"Saved evaluation results to {json_file}")
        
        # Add file paths to results
        evaluation["report_files"] = {
            "markdown": md_file,
            "json": json_file
        }
    
    return evaluation

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Evaluate Financial QA System")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--model", default="gpt-4o", help="Model to use")
    parser.add_argument("--data", help="Path to dataset file")
    parser.add_argument("--limit", type=int, default=DEFAULT_EVAL_SAMPLE_SIZE, 
                        help="Number of examples to evaluate")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        import logging
        logging.getLogger("FinancialQA").setLevel(logging.DEBUG)
    
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
    
    # Run evaluation
    print(f"Evaluating with {args.model} on {args.limit if args.limit else 'all'} examples...")
    results = run_evaluation(system, dataset, limit=args.limit)
    
    # Print summary
    print_evaluation_summary(results)
    
    # Print report path
    if "report_files" in results:
        print(f"\nDetailed report saved to: {results['report_files']['markdown']}")
    
    return results

if __name__ == "__main__":
    main()