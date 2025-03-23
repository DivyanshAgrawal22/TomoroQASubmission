# Financial QA System Evaluation Report

## Overview

- **Evaluation ID**: 20250323_180657
- **Total examples evaluated**: 10
- **Date**: 2025-03-23 18:07:45
- **Model**: gpt-4o

## Performance Metrics

- **Overall accuracy**: 30.00%
- **Exact match rate**: 30.00%
- **Correct answers**: 3/10 (30.00%)
  - **Exact matches**: 3/10 (30.00%)
  - **Close matches**: 0/10 (0.00%)
- **Incorrect answers**: 7/10 (70.00%)
- **Mean Absolute Percentage Error (MAPE)**: 57.50%

            ## Token Usage and Cost

            - **Prompt tokens**: 15,464
            - **Completion tokens**: 4,416
            - **Total tokens**: 19,880
        - **Estimated cost**: $0.0828

## Performance by Question Type

- **percentage**: 25.00% (1/4)
- **change**: 33.33% (1/3)
- **factual**: 33.33% (1/3)

## Performance by Question Difficulty

- **simple**: 0.00% (0/1)
- **moderate**: 50.00% (1/2)
- **complex**: 28.57% (2/7)

            ## Response Time Statistics

            - **Mean**: 3.39 seconds
            - **Median**: 3.22 seconds
            - **Min**: 2.66 seconds
            - **Max**: 5.22 seconds
            - **90th percentile**: 3.87 seconds
            - **95th percentile**: 4.55 seconds
        
## Error Analysis

### Common Error Types

- **Missing percentage symbol**: 2 occurrences (28.6% of errors)
- **Major calculation error (difference of 99.60, 200.0% off)**: 1 occurrences (14.3% of errors)
- **Minor calculation error (difference of 0.10, 2.9% off)**: 1 occurrences (14.3% of errors)
- **Major calculation error (difference of 1049996392.00, 100.0% off)**: 1 occurrences (14.3% of errors)
- **Unknown error type**: 1 occurrences (14.3% of errors)

            ## Sample Correct Answers

        ### Example 1

                **Question**: what was the percentage change in the redeemable noncontrolling interests from 2009 to 2010

                **Ground Truth**: 6.1%

                **Prediction**: 6.1%

                **Normalized Values**:
                - Ground Truth: 6.1%
                - Prediction: 6.1%

                **Category**: exact_match

                ---

            ### Example 2

                **Question**: what is the growth rate in the balance of unrecognized tax benefits during 2010?

                **Ground Truth**: -28.0%

                **Prediction**: -28.0%

                **Normalized Values**:
                - Ground Truth: -28.0%
                - Prediction: -28.0%

                **Category**: exact_match

                ---

            ### Example 3

                **Question**: what is the roi of an investment in s&p500 index from 2011 to 2012?

                **Ground Truth**: 16%

                **Prediction**: 16.0%

                **Normalized Values**:
                - Ground Truth: 16.0%
                - Prediction: 16.0%

                **Category**: exact_match

                ---

            
            ## Sample Incorrect Answers

        ### Example 1

                **Question**: by what percentage did the average crack spread for sweet/sour differential decrease from 2007 to 2009?

                **Ground Truth**: -49.8%

                **Prediction**: 49.8%

                **Normalized Values**:
                - Ground Truth: -49.8%
                - Prediction: 49.8%

                **Error Analysis**: 
                - Major calculation error (difference of 99.60, 200.0% off)

                ---

            ### Example 2

                **Question**: what is the growth rate of revenue from 2007 to 2008?

                **Ground Truth**: 3.5%

                **Prediction**: 3.6%

                **Normalized Values**:
                - Ground Truth: 3.5%
                - Prediction: 3.6%

                **Error Analysis**: 
                - Minor calculation error (difference of 0.10, 2.9% off)

                ---

            ### Example 3

                **Question**: based on the calculated increase in locomotive diesel fuel price in 2012 , what is the estimated total fuel cost for 2012?

                **Ground Truth**: 1050000000

                **Prediction**: $3,608 million

                **Normalized Values**:
                - Ground Truth: 1050000000.0
                - Prediction: 3608

                **Error Analysis**: 
                - Major calculation error (difference of 1049996392.00, 100.0% off)

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
    