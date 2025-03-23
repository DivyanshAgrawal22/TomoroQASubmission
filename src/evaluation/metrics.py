"""
Evaluation metrics for the Financial QA system
"""
from typing import Dict, List, Any
import numpy as np
from collections import Counter, defaultdict
import re
from utils.text_processing import normalize_answer, is_numeric_answer, extract_numeric_value, are_numerically_close
from config import NUMERIC_COMPARISON_TOLERANCE

def calculate_accuracy(correct: int, total: int) -> float:
    """
    Calculate accuracy
    
    Args:
        correct: Number of correct predictions
        total: Total number of predictions
        
    Returns:
        Accuracy as a percentage
    """
    return (correct / total * 100) if total > 0 else 0.0

def calculate_f1_score(precision: float, recall: float) -> float:
    """
    Calculate F1 score
    
    Args:
        precision: Precision value
        recall: Recall value
        
    Returns:
        F1 score
    """
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

def calculate_mape(ground_truths: List[float], predictions: List[float]) -> float:
    """
    Calculate Mean Absolute Percentage Error
    
    Args:
        ground_truths: List of ground truth values
        predictions: List of predicted values
        
    Returns:
        MAPE value
    """
    if not ground_truths or not predictions or len(ground_truths) != len(predictions):
        return 0.0
    
    # Filter out pairs where ground truth is zero to avoid division by zero
    filtered_pairs = [(gt, pred) for gt, pred in zip(ground_truths, predictions) if abs(gt) > 1e-10]
    
    if not filtered_pairs:
        return 0.0
    
    absolute_percentage_errors = [abs((gt - pred) / gt) * 100 for gt, pred in filtered_pairs]
    return sum(absolute_percentage_errors) / len(absolute_percentage_errors)

def create_confusion_matrix(actual_categories: List[str], predicted_categories: List[str]) -> Dict[str, Dict[str, int]]:
    """
    Create a confusion matrix for categorical predictions
    
    Args:
        actual_categories: List of actual categories
        predicted_categories: List of predicted categories
        
    Returns:
        Confusion matrix as nested dictionary
    """
    confusion_matrix = defaultdict(lambda: defaultdict(int))
    
    # Get unique categories
    all_categories = list(set(actual_categories + predicted_categories))
    
    # Initialize confusion matrix
    for actual in all_categories:
        for predicted in all_categories:
            confusion_matrix[actual][predicted] = 0
    
    # Populate confusion matrix
    for actual, predicted in zip(actual_categories, predicted_categories):
        confusion_matrix[actual][predicted] += 1
    
    return dict(confusion_matrix)

def categorize_prediction_result(ground_truth: str, prediction: str) -> str:
    """
    Categorize the prediction result 
    
    Args:
        ground_truth: Ground truth answer
        prediction: Predicted answer
        
    Returns:
        Category: "exact_match", "close_match", or "incorrect"
    """
    # Normalize answers for comparison
    norm_ground_truth = normalize_answer(ground_truth)
    norm_prediction = normalize_answer(prediction)
    
    # Check for exact match
    if norm_ground_truth == norm_prediction:
        return "exact_match"
    
    # For numeric answers, check if they're close enough
    if is_numeric_answer(norm_ground_truth) and is_numeric_answer(norm_prediction):
        if are_numerically_close(norm_ground_truth, norm_prediction, NUMERIC_COMPARISON_TOLERANCE):
            return "close_match"
    
    return "incorrect"

def analyze_error(ground_truth: str, prediction: str) -> str:
    """
    Analyze the error between ground truth and prediction
    
    Args:
        ground_truth: Ground truth answer
        prediction: Predicted answer
        
    Returns:
        Error analysis string
    """
    if categorize_prediction_result(ground_truth, prediction) != "incorrect":
        return None
    
    norm_ground_truth = normalize_answer(ground_truth)
    norm_prediction = normalize_answer(prediction)
    
    if is_numeric_answer(norm_ground_truth) and is_numeric_answer(norm_prediction):
        # Extract numeric values
        try:
            gt_value = extract_numeric_value(norm_ground_truth)
            pred_value = extract_numeric_value(norm_prediction)
            
            if gt_value is None or pred_value is None:
                return "Failed to extract numeric values"
            
            # Calculate difference
            abs_diff = abs(gt_value - pred_value)
            rel_diff = abs_diff / max(abs(gt_value), 1e-10)
            
            if rel_diff < 0.1:  # Within 10%
                return f"Minor calculation error (difference of {abs_diff:.2f}, {rel_diff*100:.1f}% off)"
            elif rel_diff < 0.5:  # Within 50%
                return f"Significant calculation error (difference of {abs_diff:.2f}, {rel_diff*100:.1f}% off)"
            else:
                return f"Major calculation error (difference of {abs_diff:.2f}, {rel_diff*100:.1f}% off)"
        except:
            return "Failed to compare numeric values"
    
    # Check for formatting issues
    if norm_ground_truth.replace(".", "").replace("%", "").strip() == norm_prediction.replace(".", "").replace("%", "").strip():
        return "Formatting difference"
        
    # Check for % symbol
    if "%" in norm_ground_truth and "%" not in norm_prediction:
        return "Missing percentage symbol"
    
    # Check for wrong unit
    if ("million" in ground_truth.lower() and "million" not in prediction.lower()) or \
       ("billion" in ground_truth.lower() and "billion" not in prediction.lower()):
        return "Incorrect unit"
    
    # Check for sign error
    if is_numeric_answer(norm_ground_truth) and is_numeric_answer(norm_prediction):
        gt_value = extract_numeric_value(norm_ground_truth)
        pred_value = extract_numeric_value(norm_prediction)
        if gt_value is not None and pred_value is not None:
            if (gt_value > 0 and pred_value < 0) or (gt_value < 0 and pred_value > 0):
                return "Sign error"
    
    # Default error analysis
    return "Unknown error type"

def categorize_difficulty(question: str) -> str:
    """
    Categorize question difficulty
    
    Args:
        question: The question string
        
    Returns:
        Difficulty category: "simple", "moderate", or "complex"
    """
    question_lower = question.lower()
    
    # Count number of operations required
    operation_keywords = [
        "increase", "decrease", "change", "growth", "difference",
        "percentage", "percent", "ratio", "compare", 
        "total", "sum", "average", "mean", "median"
    ]
    
    operation_count = sum(1 for keyword in operation_keywords if keyword in question_lower)
    
    # Questions with multiple years or time periods are more complex
    has_multiple_years = len(re.findall(r'\b(19|20)\d{2}\b', question)) > 1
    
    # Questions requiring calculation across different sections of a table are complex
    complex_patterns = [
        r"(difference|change).+between",
        r"compare.+and",
        r"calculate.+(percentage|percent|ratio)",
        r"what.+(percentage|percent)",
        r"how much did.+(change|increase|decrease)",
        r"year(-|\s)over(-|\s)year"
    ]
    
    is_complex_pattern = any(re.search(pattern, question_lower) for pattern in complex_patterns)
    
    # Categorize based on the complexity indicators
    if operation_count > 1 or has_multiple_years or is_complex_pattern:
        return "complex"
    elif operation_count == 1:
        return "moderate"
    else:
        return "simple"

def calculate_binned_accuracy(evaluation_results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Calculate accuracy binned by question difficulty
    
    Args:
        evaluation_results: List of evaluation result details
        
    Returns:
        Dictionary with accuracy metrics by difficulty
    """
    bins = {
        "simple": {"total": 0, "correct": 0},
        "moderate": {"total": 0, "correct": 0},
        "complex": {"total": 0, "correct": 0}
    }
    
    for result in evaluation_results:
        if "question" not in result:
            continue
            
        difficulty = categorize_difficulty(result["question"])
        bins[difficulty]["total"] += 1
        
        if result.get("is_correct", False):
            bins[difficulty]["correct"] += 1
    
    # Calculate accuracy for each bin
    for difficulty, counts in bins.items():
        if counts["total"] > 0:
            counts["accuracy"] = counts["correct"] / counts["total"] * 100
        else:
            counts["accuracy"] = 0.0
    
    return bins

def calculate_response_time_stats(processing_times: List[float]) -> Dict[str, float]:
    """
    Calculate response time statistics
    
    Args:
        processing_times: List of processing times in seconds
        
    Returns:
        Dictionary with response time statistics
    """
    if not processing_times:
        return {
            "mean": 0.0,
            "median": 0.0,
            "min": 0.0,
            "max": 0.0,
            "p90": 0.0,
            "p95": 0.0
        }
    
    return {
        "mean": float(np.mean(processing_times)),
        "median": float(np.median(processing_times)),
        "min": float(np.min(processing_times)),
        "max": float(np.max(processing_times)),
        "p90": float(np.percentile(processing_times, 90)),
        "p95": float(np.percentile(processing_times, 95))
    }

def calculate_error_distribution(evaluation_results: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculate distribution of error types
    
    Args:
        evaluation_results: List of evaluation result details
        
    Returns:
        Dictionary with error type counts
    """
    error_counts = Counter()
    
    for result in evaluation_results:
        if not result.get("is_correct", True) and result.get("error_analysis"):
            error_counts[result["error_analysis"]] += 1
    
    return dict(error_counts)

def evaluate_predictions(
    ground_truths: List[str], 
    predictions: List[str], 
    questions: List[str] = None,
    processing_times: List[float] = None
) -> Dict[str, Any]:
    """
    Comprehensive evaluation of predictions
    
    Args:
        ground_truths: List of ground truth answers
        predictions: List of predicted answers
        questions: Optional list of questions
        processing_times: Optional list of processing times
        
    Returns:
        Dictionary with evaluation metrics
    """
    total = len(ground_truths)
    if total == 0 or len(predictions) != total:
        return {"error": "Input lists must be non-empty and of equal length"}
    
    # Initialize result categories
    results = {
        "exact_match": 0,
        "close_match": 0,
        "incorrect": 0
    }
    
    # Detailed results for each prediction
    details = []
    
    for i in range(total):
        ground_truth = ground_truths[i]
        prediction = predictions[i]
        
        # Create result entry
        result = {
            "ground_truth": ground_truth,
            "prediction": prediction,
            "normalized_ground_truth": normalize_answer(ground_truth),
            "normalized_prediction": normalize_answer(prediction),
        }
        
        # Add question if available
        if questions and i < len(questions):
            result["question"] = questions[i]
        
        # Add processing time if available
        if processing_times and i < len(processing_times):
            result["processing_time"] = processing_times[i]
        
        # Categorize prediction
        category = categorize_prediction_result(ground_truth, prediction)
        result["category"] = category
        result["is_correct"] = category in ["exact_match", "close_match"]
        
        # Add error analysis for incorrect predictions
        if category == "incorrect":
            result["error_analysis"] = analyze_error(ground_truth, prediction)
        
        # Increment category counter
        results[category] += 1
        
        # Add to details
        details.append(result)
    
    # Calculate overall metrics
    correct = results["exact_match"] + results["close_match"]
    accuracy = calculate_accuracy(correct, total)
    exact_match_rate = calculate_accuracy(results["exact_match"], total)
    
    # Extract numeric values for MAPE calculation
    numeric_gts = []
    numeric_preds = []
    
    for i in range(total):
        gt = extract_numeric_value(normalize_answer(ground_truths[i]))
        pred = extract_numeric_value(normalize_answer(predictions[i]))
        if gt is not None and pred is not None:
            numeric_gts.append(gt)
            numeric_preds.append(pred)
    
    # Calculate MAPE if we have numeric values
    mape = calculate_mape(numeric_gts, numeric_preds) if numeric_gts else None
    
    # Calculate additional metrics if questions are available
    additional_metrics = {}
    
    if questions:
        # Binned accuracy by difficulty
        additional_metrics["difficulty_bins"] = calculate_binned_accuracy(details)
        
        # Confusion matrix for question types
        from config import QUESTION_TYPES
        actual_categories = []
        predicted_categories = []
        
        for result in details:
            if "is_correct" in result:
                actual_categories.append("correct" if result["is_correct"] else "incorrect")
                predicted_categories.append(result["category"])
        
        additional_metrics["confusion_matrix"] = create_confusion_matrix(
            actual_categories, predicted_categories)
    
    # Response time statistics
    if processing_times:
        additional_metrics["response_time"] = calculate_response_time_stats(processing_times)
    
    # Error type distribution
    error_distribution = calculate_error_distribution(details)
    
    # Combine all metrics
    metrics = {
        "total": total,
        "correct": correct,
        "exact_match": results["exact_match"],
        "close_match": results["close_match"],
        "incorrect": results["incorrect"],
        "accuracy": accuracy,
        "exact_match_rate": exact_match_rate,
        "mape": mape,
        "error_distribution": error_distribution,
        "details": details
    }
    
    # Add additional metrics
    metrics.update(additional_metrics)
    
    return metrics