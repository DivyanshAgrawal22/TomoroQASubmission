# Financial QA System Evaluation Report

## Overview

- **Evaluation ID**: 20250323_172712
- **Total examples evaluated**: 10
- **Date**: 2025-03-23 17:28:13
- **Model**: gpt-4o

## Performance Metrics

- **Overall accuracy**: 40.00%
- **Exact match rate**: 40.00%
- **Correct answers**: 4/10 (40.00%)
  - **Exact matches**: 4/10 (40.00%)
  - **Close matches**: 0/10 (0.00%)
- **Incorrect answers**: 6/10 (60.00%)
- **Mean Absolute Percentage Error (MAPE)**: 33.75%

## Token Usage and Cost

- **Prompt tokens**: 17,170
- **Completion tokens**: 4,919
- **Total tokens**: 22,089
- **Estimated cost**: $0.0921

## Performance by Question Type

- **percentage**: 16.67% (1/6)
- **other**: 66.67% (2/3)
- **factual**: 100.00% (1/1)

## Performance by Question Difficulty

- **simple**: 100.00% (1/1)
- **moderate**: 50.00% (1/2)
- **complex**: 28.57% (2/7)

## Response Time Statistics

- **Mean**: 4.55 seconds
- **Median**: 3.39 seconds
- **Min**: 3.05 seconds
- **Max**: 12.97 seconds
- **90th percentile**: 6.71 seconds
- **95th percentile**: 9.84 seconds

## Error Analysis

### Common Error Types

- **Missing percentage symbol**: 4 occurrences (66.7% of errors)
- **Minor calculation error (difference of 0.80, 2.5% off)**: 1 occurrences (16.7% of errors)
- **Major calculation error (difference of 52.40, 200.0% off)**: 1 occurrences (16.7% of errors)

## Sample Correct Answers

### Example 1

**Question**: what was the percentage change in the net cash from operating activities from 2008 to 2009

**Ground Truth**: 14.1%

**Prediction**: 14.1%

**Normalized Values**:
- Ground Truth: 14.1%
- Prediction: 14.1%

**Category**: exact_match

---

### Example 2

**Question**: what portion of total obligations are due within the next 3 years?

**Ground Truth**: 22.99%

**Prediction**: 23.0%

**Normalized Values**:
- Ground Truth: 23.0%
- Prediction: 23.0%

**Category**: exact_match

---

### Example 3

**Question**: for the years ended december 31 , 2013 , 2012 and 2011 , what was the total in millions capitalized to assets associated with compensation expense related to long-term compensation plans , restricted stock and stock options?\\n

**Ground Truth**: 12

**Prediction**: $12.0 million

**Normalized Values**:
- Ground Truth: 12.0
- Prediction: 12.0

**Category**: exact_match

---


## Sample Incorrect Answers

### Example 1

**Question**: what was the percent of the growth in the revenues from 2007 to 2008

**Ground Truth**: 1.3%

**Prediction**: **

**Normalized Values**:
- Ground Truth: 1.3%
- Prediction: 

**Error Analysis**: 
- Missing percentage symbol

---

### Example 2

**Question**: what was the percentage change in net sales from 2000 to 2001?

**Ground Truth**: -32%

**Prediction**: -32.8%

**Normalized Values**:
- Ground Truth: -32.0%
- Prediction: -32.8%

**Error Analysis**: 
- Minor calculation error (difference of 0.80, 2.5% off)

---

### Example 3

**Question**: what was the difference in percentage cumulative return on investment for united parcel service inc . compared to the s&p 500 index for the five year period ended 12/31/09?

**Ground Truth**: -26.16%

**Prediction**: 26.2%

**Normalized Values**:
- Ground Truth: -26.2%
- Prediction: 26.2%

**Error Analysis**: 
- Major calculation error (difference of 52.40, 200.0% off)

---


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
