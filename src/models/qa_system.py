"""
Financial QA System
"""
import time
from typing import Dict, List, Any
from openai import OpenAI

from config import DEFAULT_MODEL, EXTRACTION_MODEL, SYSTEM_PROMPT, COST_PER_1K
from utils.logging_utils import setup_logging
from data.document_utils import format_document_context, extract_document_source

# Setup logger
logger = setup_logging("QASystem")

class FinancialQASystem:
    """Financial QA System using OpenAI API"""
    
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        """
        Initialize the Financial QA System
        
        Args:
            api_key: OpenAI API key
            model: Model to use for requests
        """
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        
        # Track token usage and cost
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        
        # Debug properties
        self._current_question = ""
        self._last_response = ""
        
        logger.info(f"Initialized QA system with model: {model}")
    
    def debug_direct(self, response_text: str, processed_answer: str):
        """
        Print direct debug information to console
        
        Args:
            response_text: Raw response text
            processed_answer: Processed answer
        """
        print("\n" + "=" * 50)
        print("DIRECT DEBUG OUTPUT")
        print("=" * 50)
        print("First 300 characters of response:")
        print(response_text[:300])
        print("\nProcessed answer:")
        print(processed_answer)
        print("=" * 50)
    
    def answer_question(self, document: Dict[str, Any], question: str) -> Dict[str, Any]:
        """
        Answer a question about a financial document
        
        Args:
            document: The financial document data
            question: The question to answer
            
        Returns:
            Dictionary with answer and reasoning
        """
        # Store current question for extraction context
        self._current_question = question

        # Format document context
        document_context = format_document_context(document)
        
        # Generate answer with reasoning
        prompt = f"""
            Answer the following question about a financial document:

            Question: {question}

            Document content:
            {document_context}

            First, analyze the question to determine what information is needed and what calculations (if any) must be performed.
            Then, extract the relevant data from the document.
            Finally, provide a detailed answer with step-by-step reasoning.

            For percentage calculations, ensure the final answer is formatted with one decimal place (e.g., "14.1%").
            For currency values, use appropriate formatting (e.g., "$1.2 million").

            At the end, please provide a clear and concise final answer in a single line, preceded by "Final Answer:".
        """
        
        # Get response from OpenAI
        logger.info(f"Sending request to OpenAI API for question: {question}")
        start_time = time.time()
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Received response in {elapsed_time:.2f} seconds")
        
        # Update token usage
        if hasattr(response, 'usage') and response.usage:
            self.token_usage["prompt_tokens"] += response.usage.prompt_tokens
            self.token_usage["completion_tokens"] += response.usage.completion_tokens
            self.token_usage["total_tokens"] += response.usage.total_tokens
            
            logger.info(f"Token usage: {response.usage.prompt_tokens} prompt, {response.usage.completion_tokens} completion")
        
        answer_text = response.choices[0].message.content
        self._last_response = answer_text
        
        # Debug the full response
        logger.debug(f"Full response from OpenAI: {answer_text[:500]}...")
        
        # Extract the final answer and reasoning steps
        final_answer = self._extract_final_answer(answer_text)
        # Add direct debug call
        self.debug_direct(answer_text, final_answer)
        reasoning_steps = self._extract_reasoning_steps(answer_text)
        
        # Extract document source information
        source_info = extract_document_source(document)
        
        return {
            "answer": final_answer,
            "reasoning": reasoning_steps,
            "full_response": answer_text,
            "source": source_info,
            "processing_time": elapsed_time
        }
    
    def extract_with_llm(self, text: str, extraction_type: str, question: str) -> str:
        """
        Use LLM to extract specific information from text
        
        Args:
            text: The text to extract from
            extraction_type: Type of extraction (final_answer, reasoning_steps)
            question: Original question for context
            
        Returns:
            Extracted information
        """
        prompt_templates = {
            "final_answer": """
                Extract the final answer from the following text that responds to the question: "{question}"
                
                {text}
                
                Return ONLY the final answer as a concise, single phrase or value, with no additional explanation or context.
                For percentage values, ensure the answer has exactly one decimal place (e.g., "14.1%" not "14.10%").
                For currency values, use appropriate formatting (e.g., "$1.2 million").
            """,
            "reasoning_steps": """
                Extract the reasoning steps from the following text that explains the answer to: "{question}"
                
                {text}
                
                Return a list of the key reasoning steps, with each step on a new line starting with "- ".
                Focus on extracting the analytical process, not the final conclusion.
            """,
            "error_analysis": """
                Compare the following predicted answer with the ground truth for the question: "{question}"
                
                Ground truth: {ground_truth}
                Prediction: {prediction}
                
                Analyze why the prediction might be incorrect and provide a concise error category (e.g., "calculation error", 
                "missing percentage symbol", "wrong reference year", etc.)
                Return ONLY the error category as a brief phrase.
            """
        }
        
        if extraction_type not in prompt_templates:
            return "Unsupported extraction type"
        
        # Prepare the prompt with the template
        prompt = prompt_templates[extraction_type].format(
            text=text, 
            question=question,
            ground_truth=getattr(self, '_ground_truth', ''),
            prediction=getattr(self, '_prediction', '')
        )
        
        # Get response from OpenAI
        try:
            response = self.client.chat.completions.create(
                model=EXTRACTION_MODEL,  # Use a smaller model to save costs
                messages=[
                    {"role": "system", "content": "You are a precise extraction assistant that provides concise, accurate responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            extraction = response.choices[0].message.content.strip()
            
            # Update token usage
            if hasattr(response, 'usage') and response.usage:
                self.token_usage["prompt_tokens"] += response.usage.prompt_tokens
                self.token_usage["completion_tokens"] += response.usage.completion_tokens
                self.token_usage["total_tokens"] += response.usage.total_tokens
            
            return extraction
        
        except Exception as e:
            logger.error(f"Error using LLM for extraction: {e}")
            return "Extraction failed"

    def _extract_final_answer(self, text: str) -> str:
        """Extract the final answer from the response text using regex or LLM"""
        if not text or text.strip() == "":
            return "No response received from the model."
        
        # Try to find "Final Answer:" in the text
        import re
        final_answer_match = re.search(r"Final Answer:\s*(.+?)(?:\n|$)", text)
        if final_answer_match:
            return final_answer_match.group(1).strip()
        
        # If not found, use LLM for extraction
        extracted = self.extract_with_llm(text, "final_answer", self._current_question)
        
        # If the LLM extraction returns something useful
        if extracted and len(extracted) > 0 and extracted != "Extraction failed":
            return extracted

        return "Could not extract a final answer"

    def _extract_reasoning_steps(self, text: str) -> List[str]:
        """Extract reasoning steps from the response text"""
        # Store the current text for debugging if needed
        self._last_reasoning_text = text
        
        # Use LLM for extraction
        extracted = self.extract_with_llm(text, "reasoning_steps", self._current_question)
        
        # If the LLM extraction returns something useful, parse it into a list
        if extracted and extracted != "Extraction failed":
            # The LLM should return a list with items starting with "- "
            if "- " in extracted:
                steps = [step.strip() for step in extracted.split("- ") if step.strip()]
                if steps:
                    return steps
                
        # As a fallback, try to split by newlines and look for numbered steps
        import re
        steps = []
        lines = text.split('\n')
        for line in lines:
            # Look for numbered steps or bullet points
            if re.match(r'^\d+[\)\.]\s+', line) or line.strip().startswith('•') or line.strip().startswith('-'):
                steps.append(line.strip())
                
        if steps:
            return steps
                
        # If all else fails, return a minimal list with the text
        return ["No step-by-step reasoning detected"]

    def get_token_usage_report(self) -> str:
        """Get a report of token usage and estimated cost"""
        cost_per_1k = COST_PER_1K.get(self.model, COST_PER_1K[DEFAULT_MODEL])
        prompt_cost = (self.token_usage["prompt_tokens"] / 1000) * cost_per_1k["prompt"]
        completion_cost = (self.token_usage["completion_tokens"] / 1000) * cost_per_1k["completion"]
        total_cost = prompt_cost + completion_cost
        
        report = f"""
            Token Usage and Cost Report:
            ---------------------------
            Model: {self.model}
            Prompt tokens: {self.token_usage["prompt_tokens"]:,}
            Completion tokens: {self.token_usage["completion_tokens"]:,}
            Total tokens: {self.token_usage["total_tokens"]:,}

            Estimated Cost:
            Prompt cost: ${prompt_cost:.4f}
            Completion cost: ${completion_cost:.4f}
            Total cost: ${total_cost:.4f}
        """
        return report

    def reset_token_usage(self):
        """Reset token usage counters"""
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }