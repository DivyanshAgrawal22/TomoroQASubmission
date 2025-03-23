"""
Reporting utilities for evaluation results
"""
from typing import Dict, Any, Tuple
from datetime import datetime
import json
import os
from config import REPORTS_DIR, CURRENT_TIMESTAMP

def generate_evaluation_report(results: Dict[str, Any], timestamp: str = None) -> str:
    """
    Generate a Markdown evaluation report
    
    Args:
        results: Evaluation results
        timestamp: Optional timestamp
        
    Returns:
        Markdown report
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report = f"""# Financial QA System Evaluation Report

## Overview

- **Evaluation ID**: {timestamp}
- **Total examples evaluated**: {results['total']}
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Model**: {results.get('model', 'GPT-4o')}

## Performance Metrics

- **Overall accuracy**: {results.get('accuracy', 0):.2f}%
- **Exact match rate**: {results.get('exact_match_rate', 0):.2f}%
- **Correct answers**: {results['correct']}/{results['total']} ({results['correct']/results['total']*100:.2f}%)
  - **Exact matches**: {results['exact_match']}/{results['total']} ({results['exact_match']/results['total']*100:.2f}%)
  - **Close matches**: {results.get('close_match', 0)}/{results['total']} ({results.get('close_match', 0)/results['total']*100:.2f}%)
- **Incorrect answers**: {results['incorrect']}/{results['total']} ({results['incorrect']/results['total']*100:.2f}%)
"""

    # Add MAPE if available
    if results.get('mape') is not None:
        report += f"- **Mean Absolute Percentage Error (MAPE)**: {results['mape']:.2f}%\n"
        
    # Add F1 Score if available
    if results.get('f1_score') is not None:
        report += f"- **F1 Score**: {results['f1_score']:.2f}\n"

    # Add token usage and cost if available
    if "token_usage" in results:
        report += f"""
            ## Token Usage and Cost

            - **Prompt tokens**: {results["token_usage"]["prompt_tokens"]:,}
            - **Completion tokens**: {results["token_usage"]["completion_tokens"]:,}
            - **Total tokens**: {results["token_usage"]["total_tokens"]:,}
        """
        if "cost" in results:
            report += f"- **Estimated cost**: ${results['cost'].get('total_cost', 0):.4f}\n"

    # Add performance by question type if available
    if "question_types" in results:
        report += "\n## Performance by Question Type\n\n"
        for q_type, stats in results["question_types"].items():
            if "accuracy" in stats:
                report += f"- **{q_type}**: {stats['accuracy']:.2f}% ({stats['correct']}/{stats['count']})\n"

    # Add performance by difficulty if available
    if "difficulty_bins" in results:
        report += "\n## Performance by Question Difficulty\n\n"
        for difficulty, stats in results["difficulty_bins"].items():
            report += f"- **{difficulty}**: {stats.get('accuracy', 0):.2f}% ({stats.get('correct', 0)}/{stats.get('total', 0)})\n"

    # Add response time statistics if available
    if "response_time" in results:
        rt = results["response_time"]
        report += f"""
            ## Response Time Statistics

            - **Mean**: {rt.get('mean', 0):.2f} seconds
            - **Median**: {rt.get('median', 0):.2f} seconds
            - **Min**: {rt.get('min', 0):.2f} seconds
            - **Max**: {rt.get('max', 0):.2f} seconds
            - **90th percentile**: {rt.get('p90', 0):.2f} seconds
            - **95th percentile**: {rt.get('p95', 0):.2f} seconds
        """

    # Add error analysis if available
    if "error_distribution" in results and results["error_distribution"]:
        report += "\n## Error Analysis\n\n"
        
        # Sort error types by frequency
        error_types = sorted(
            results["error_distribution"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        report += "### Common Error Types\n\n"
        for error_type, count in error_types[:5]:  # Top 5 error types
            percentage = count / results['incorrect'] * 100 if results['incorrect'] > 0 else 0
            report += f"- **{error_type}**: {count} occurrences ({percentage:.1f}% of errors)\n"
    
    # Sample of correct and incorrect answers
    correct_examples = []
    incorrect_examples = []
    
    if "details" in results:
        correct_examples = [d for d in results["details"] if d.get("is_correct", False)]
        incorrect_examples = [d for d in results["details"] if not d.get("is_correct", False)]
    
    # Sample of correct answers
    if correct_examples:
        report += """
            ## Sample Correct Answers

        """
        for i, example in enumerate(correct_examples[:3]):  # Show first 3 examples
            report += f"""### Example {i+1}

                **Question**: {example.get("question", "N/A")}

                **Ground Truth**: {example["ground_truth"]}

                **Prediction**: {example["prediction"]}

                **Normalized Values**:
                - Ground Truth: {example.get("normalized_ground_truth", "N/A")}
                - Prediction: {example.get("normalized_prediction", "N/A")}

                **Category**: {example.get("category", "N/A")}

                ---

            """
    
    # Sample of incorrect answers
    if incorrect_examples:
        report += """
            ## Sample Incorrect Answers

        """
        for i, example in enumerate(incorrect_examples[:3]):  # Show first 3 examples
            report += f"""### Example {i+1}

                **Question**: {example.get("question", "N/A")}

                **Ground Truth**: {example["ground_truth"]}

                **Prediction**: {example["prediction"]}

                **Normalized Values**:
                - Ground Truth: {example.get("normalized_ground_truth", "N/A")}
                - Prediction: {example.get("normalized_prediction", "N/A")}

                **Error Analysis**: 
                - {example.get("error_analysis", "No analysis available")}

                ---

            """
    
    # Conclusions and recommendations
    report += f"""
        ## Conclusions and Recommendations

        Based on the evaluation results, the following improvements could enhance the system:

        1. **Answer Normalization**: Improve the answer normalization process to better handle variations in answer formats, especially for percentages and numerical values.

        2. **Question Understanding**: Implement more sophisticated question type classification to better understand the intent behind financial questions.

        3. **Calculation Accuracy**: Add validation steps for numerical calculations, particularly for percentage changes and financial metrics.

        4. **Response Formatting**: Standardize answer formats to match the expected output format, ensuring consistent presentation of percentages and numerical values.

        ## Next Steps

        1. Fine-tune the document retrieval component to better match questions with relevant documents
        2. Implement specialized handling for different question types
        3. Add validation steps for numerical calculations
        4. Expand the evaluation to a larger and more diverse dataset
        5. Investigate the use of fine-tuned models for financial QA tasks
    """
            
    return report

def save_evaluation_report(results: Dict[str, Any], timestamp: str = None) -> Tuple[str, str]:
    """
    Save evaluation results to markdown and JSON files
    
    Args:
        results: Evaluation results
        timestamp: Optional timestamp
        
    Returns:
        Tuple with paths to markdown and JSON files
    """
    if timestamp is None:
        timestamp = CURRENT_TIMESTAMP
    
    # Ensure output directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # Generate report
    report = generate_evaluation_report(results, timestamp)
    
    # Save markdown report
    md_file = os.path.join(REPORTS_DIR, f"finqa_evaluation_{timestamp}.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    # Create a simplified version of results to avoid huge JSON files
    simplified_results = {
        "total": results["total"],
        "correct": results["correct"],
        "incorrect": results["incorrect"],
        "exact_match": results["exact_match"],
        "accuracy": results.get("accuracy", 0),
        "exact_match_rate": results.get("exact_match_rate", 0),
        "mape": results.get("mape"),
        "f1_score": results.get("f1_score"),
        "question_types": results.get("question_types", {}),
        "difficulty_bins": results.get("difficulty_bins", {}),
        "response_time": results.get("response_time", {}),
        "error_distribution": results.get("error_distribution", {}),
        "token_usage": results.get("token_usage", {}),
        "cost": results.get("cost", {}),
        # Include sample of details but not all for large datasets
        "sample_details": results["details"][:10] if len(results["details"]) > 10 else results["details"]
    }
    
    # Save JSON results
    json_file = os.path.join(REPORTS_DIR, f"finqa_results_{timestamp}.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(simplified_results, f, indent=2)
    
    return md_file, json_file

def print_evaluation_summary(results: Dict[str, Any]):
    """
    Print a summary of evaluation results to console
    
    Args:
        results: Evaluation results
    """
    print("\n===== Evaluation Results Summary =====")
    print(f"Total examples evaluated: {results['total']}")
    print(f"Accuracy: {results.get('accuracy', 0):.2f}%")
    print(f"Exact match rate: {results.get('exact_match_rate', 0):.2f}%")
    
    if results.get('mape') is not None:
        print(f"MAPE: {results['mape']:.2f}%")
    
    if results.get('f1_score') is not None:
        print(f"F1 Score: {results['f1_score']:.2f}")
    
    # Display performance by question type
    if "question_types" in results:
        print("\nPerformance by question type:")
        for q_type, stats in results["question_types"].items():
            if "accuracy" in stats:
                print(f"  {q_type}: {stats['accuracy']:.2f}% ({stats['correct']}/{stats['count']})")
    
    # Show error analysis
    if "error_distribution" in results and results["error_distribution"]:
        print("\nCommon error types:")
        error_items = sorted(results["error_distribution"].items(), key=lambda x: x[1], reverse=True)
        for error_type, count in error_items[:5]:  # Top 5 error types
            print(f"  {error_type}: {count} occurrences")
    
    # Show token usage and cost
    if "token_usage" in results:
        print("\nToken usage:")
        print(f"  Prompt tokens: {results['token_usage']['prompt_tokens']:,}")
        print(f"  Completion tokens: {results['token_usage']['completion_tokens']:,}")
        print(f"  Total tokens: {results['token_usage']['total_tokens']:,}")
        
        if "cost" in results:
            print(f"  Estimated cost: ${results['cost'].get('total_cost', 0):.4f}")
    
    print("=" * 40)