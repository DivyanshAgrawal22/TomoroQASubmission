# Financial QA System Evaluation Report

## Overview

- **Evaluation ID**: 20250323_192037
- **Total examples evaluated**: 2109
- **Date**: 2025-03-23 22:14:21
- **Model**: gpt-4o

## Performance Metrics

- **Overall accuracy**: 47.61%
- **Exact match rate**: 32.86%
- **Correct answers**: 1004/2109 (47.61%)
  - **Exact matches**: 693/2109 (32.86%)
  - **Close matches**: 311/2109 (14.75%)
- **Incorrect answers**: 1105/2109 (52.39%)
- **Mean Absolute Percentage Error (MAPE)**: 1216462.84%

            ## Token Usage and Cost

            - **Prompt tokens**: 3,374,797
            - **Completion tokens**: 949,323
            - **Total tokens**: 4,324,120
        - **Estimated cost**: $17.9302

## Performance by Question Type

- **quantity**: 34.09% (15/44)
- **percentage**: 45.59% (522/1145)
- **factual**: 56.99% (269/472)
- **change**: 43.51% (161/370)
- **other**: 46.05% (35/76)
- **explanation**: 100.00% (2/2)

## Performance by Question Difficulty

- **simple**: 37.98% (49/129)
- **moderate**: 59.56% (190/319)
- **complex**: 46.06% (765/1661)

            ## Response Time Statistics

            - **Mean**: 3.52 seconds
            - **Median**: 3.20 seconds
            - **Min**: 1.81 seconds
            - **Max**: 16.26 seconds
            - **90th percentile**: 4.62 seconds
            - **95th percentile**: 5.76 seconds
        
## Error Analysis

### Common Error Types

- **Missing percentage symbol**: 545 occurrences (49.3% of errors)
- **Unknown error type**: 92 occurrences (8.3% of errors)
- **Minor calculation error (difference of 0.50, 1.4% off)**: 3 occurrences (0.3% of errors)
- **Minor calculation error (difference of 0.10, 1.7% off)**: 3 occurrences (0.3% of errors)
- **Minor calculation error (difference of 0.10, 1.4% off)**: 3 occurrences (0.3% of errors)

            ## Sample Correct Answers

        ### Example 1

                **Question**: how much were investment advisory revenues in 2007 , in millions of dollars?

                **Ground Truth**: 1878

                **Prediction**: $1,878 million

                **Normalized Values**:
                - Ground Truth: 1878.0
                - Prediction: 1878

                **Category**: close_match

                ---

            ### Example 2

                **Question**: what was the percentage change in total interest payments from 2009 to 2010?

                **Ground Truth**: -6%

                **Prediction**: -6.0%

                **Normalized Values**:
                - Ground Truth: -6.0%
                - Prediction: -6.0%

                **Category**: exact_match

                ---

            ### Example 3

                **Question**: what was the percentage increase in the total assets from 2007 to 2008

                **Ground Truth**: 2.6%

                **Prediction**: 2.6%

                **Normalized Values**:
                - Ground Truth: 2.6%
                - Prediction: 2.6%

                **Category**: exact_match

                ---

            
            ## Sample Incorrect Answers

        ### Example 1

                **Question**: what was the percent of the change in income from cash and cash investments from 2010 to 2011

                **Ground Truth**: 33.3%

                **Prediction**: **

                **Normalized Values**:
                - Ground Truth: 33.3%
                - Prediction: 

                **Error Analysis**: 
                - Missing percentage symbol

                ---

            ### Example 2

                **Question**: what was the percentage change in cash provided by operating activities between 2004 and 2005?

                **Ground Truth**: 15%

                **Prediction**: **

                **Normalized Values**:
                - Ground Truth: 15.0%
                - Prediction: 

                **Error Analysis**: 
                - Missing percentage symbol

                ---

            ### Example 3

                **Question**: what was average percentage for lifo inventories of consolidated inventories for december 31 , 2017 and 2016?

                **Ground Truth**: 39.5%

                **Prediction**: **

                **Normalized Values**:
                - Ground Truth: 39.5%
                - Prediction: 

                **Error Analysis**: 
                - Missing percentage symbol

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
    