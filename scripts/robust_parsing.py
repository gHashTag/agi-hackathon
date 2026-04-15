#!/usr/bin/env python3
"""
Robust Answer Parser for AGI Hackathon Evaluation
Provides multiple fallback patterns for answer and confidence extraction
with proper validation to prevent measurement errors.

Author: AGI Hackathon Team
Date: 2026-04-15
"""

import re
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class ParsedAnswer:
    """Result of parsing a model response"""
    answer: str  # A, B, C, or D
    confidence: int  # 0-100
    reasoning: str
    extraction_method: str  # Which pattern matched
    is_valid: bool  # Whether extraction was valid
    warning: Optional[str]  # Any warnings about the extraction


class RobustAnswerParser:
    """
    Robust parser for extracting answers from LLM responses.
    Uses multiple fallback patterns with validation to prevent measurement errors.
    """

    # Answer extraction patterns in priority order
    ANSWER_PATTERNS = [
        # Pattern 1: Standard format (highest priority)
        (r'Answer:\s*([A-D])', 'standard_format', 100),

        # Pattern 2: "The answer is" format
        (r'The\s+answer\s+is\s*:?\s*([A-D])', 'the_answer_is', 90),

        # Pattern 3: "Correct:" format
        (r'Correct\s*:?\s*([A-D])', 'correct_format', 85),

        # Pattern 4: Therefore/thus/consequently followed by letter (needs to be after more specific patterns)
        # Note: This pattern is lenient, so check after trying more specific patterns first
        (r'(?:Therefore|Thus|Consequently|So)[\s,\w]+(?:the\s+answer\s+is\s+)?([A-D])\b', 'reasoning_conclusion', 75),

        # Pattern 5: Choice letter with context (most lenient)
        (r'(?:Choice|Option|Answer)\s*[:\(]\s*([A-D])', 'choice_format', 70),
    ]

    # Confidence extraction patterns
    CONFIDENCE_PATTERNS = [
        # Pattern 1: Standard "Confidence: X" format
        (r'Confidence:\s*(\d+)\s*%?', 'confidence_colon', 100),

        # Pattern 2: "X% confident" format
        (r'(\d+)\s*%\s*(?:very|fairly|somewhat|highly)?\s*confident', 'percentage_confident', 90),

        # Pattern 3: Verbal expressions
        (r'Confidence:\s*(very\s+high|very\s+confident|extremely\s+confident)', 'verbal_very_high', 95),
        (r'Confidence:\s*(high|confident)', 'verbal_high', 80),
        (r'Confidence:\s*(fairly\s+high|fairly\s+confident)', 'verbal_fairly_high', 75),
        (r'Confidence:\s*(medium|moderate)', 'verbal_medium', 60),
        (r'Confidence:\s*(fairly\s+low|fairly\s+uncertain)', 'verbal_fairly_low', 45),
        (r'Confidence:\s*(low|uncertain|guessing)', 'verbal_low', 30),
        (r'Confidence:\s*(very\s+low|very\s+uncertain|essentially\s+guessing)', 'verbal_very_low', 20),
    ]

    # Verbal confidence to numeric mapping
    VERBAL_CONFIDENCE_MAP = {
        'very_high': 95,
        'high': 80,
        'fairly_high': 75,
        'medium': 60,
        'fairly_low': 45,
        'low': 30,
        'very_low': 20,
    }

    def __init__(self):
        """Initialize parser"""
        self.last_answer_pattern = None
        self.last_confidence_pattern = None

    def extract_answer(self, text: str, valid_choices: list = None) -> Tuple[str, str, bool, Optional[str]]:
        """
        Extract answer from text using multiple fallback patterns.

        Args:
            text: Model response text
            valid_choices: List of valid choice letters (default: ['A', 'B', 'C', 'D'])

        Returns:
            Tuple of (answer, extraction_method, is_valid, warning)
        """
        if valid_choices is None:
            valid_choices = ['A', 'B', 'C', 'D']

        # Try each pattern in priority order
        for pattern, method_name, priority in self.ANSWER_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                answer = match.group(1).upper()

                # Validate answer
                if answer not in valid_choices:
                    return 'A', method_name, False, f"Extracted '{answer}' not in valid choices"

                # Check if extracted from context (suspicious if first occurrence)
                first_occurrence = text.find(answer)
                if first_occurrence < len(text) * 0.3:  # In first 30% of text
                    return answer, method_name, True, f"Answer found early in response (position {first_occurrence})"

                self.last_answer_pattern = method_name
                return answer, method_name, True, None

        # Fallback: Extract first valid letter from context
        for choice in valid_choices:
            if re.search(rf'\b{choice}\b', text):
                self.last_answer_pattern = 'fallback_context'
                return choice, 'fallback_context', True, "Used fallback extraction from context"

        # Ultimate fallback: Return A with warning
        return 'A', 'ultimate_fallback', False, "No answer pattern matched, used ultimate fallback to 'A'"

    def extract_confidence(self, text: str) -> Tuple[int, str, Optional[str]]:
        """
        Extract confidence score from text using multiple formats.

        Args:
            text: Model response text

        Returns:
            Tuple of (confidence, extraction_method, warning)
        """
        # Try each pattern in priority order
        for pattern, method_name, priority in self.CONFIDENCE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'verbal' in method_name:
                    # Map verbal to numeric
                    verbal_key = match.group(1).lower().replace(' ', '_')
                    if verbal_key in self.VERBAL_CONFIDENCE_MAP:
                        confidence = self.VERBAL_CONFIDENCE_MAP[verbal_key]
                    else:
                        confidence = 50  # Default for unknown verbal expressions
                else:
                    confidence = int(match.group(1))

                # Clamp to valid range
                confidence = max(0, min(100, confidence))

                self.last_confidence_pattern = method_name
                return confidence, method_name, None

        # Fallback: Return default confidence with warning
        return 50, 'fallback_50', "No confidence pattern matched, used default 50"

    def extract_reasoning(self, text: str, max_length: int = 1000) -> str:
        """
        Extract reasoning from response text.

        Args:
            text: Model response text
            max_length: Maximum length of reasoning to extract

        Returns:
            Extracted reasoning text
        """
        # Try to extract reasoning section
        patterns = [
            r'Reasoning:\s*(.+?)(?=\n\n|---|$)',
            r'(?:Reason|Explanation|Because)[\s,:]\s*(.+?)(?=\n\n|Answer|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                reasoning = match.group(1).strip()
                # Limit length
                if len(reasoning) > max_length:
                    reasoning = reasoning[:max_length] + '...'
                return reasoning

        # Fallback: Return text before answer
        if 'Answer:' in text:
            reasoning = text.split('Answer:')[0].strip()
            return reasoning[:max_length] if len(reasoning) > max_length else reasoning

        return text[:max_length] if len(text) > max_length else text

    def parse(self, text: str, valid_choices: list = None) -> ParsedAnswer:
        """
        Parse complete response with answer, confidence, and reasoning.

        Args:
            text: Model response text
            valid_choices: List of valid choice letters

        Returns:
            ParsedAnswer object with all extracted information
        """
        # Extract answer
        answer, ans_method, ans_valid, ans_warning = self.extract_answer(text, valid_choices)

        # Extract confidence
        confidence, conf_method, conf_warning = self.extract_confidence(text)

        # Extract reasoning
        reasoning = self.extract_reasoning(text)

        # Combine warnings
        warnings = []
        if ans_warning:
            warnings.append(ans_warning)
        if conf_warning:
            warnings.append(conf_warning)

        # Determine overall validity
        is_valid = ans_valid

        return ParsedAnswer(
            answer=answer,
            confidence=confidence,
            reasoning=reasoning,
            extraction_method=f"{ans_method}|{conf_method}",
            is_valid=is_valid,
            warning='; '.join(warnings) if warnings else None
        )


def test_parser():
    """Test the robust parser with diverse responses"""
    parser = RobustAnswerParser()

    test_cases = [
        # Standard format
        """
        ---
        Answer: B
        Confidence: 85
        Reasoning: The pattern shows X followed by Y...
        ---
        """,

        # "The answer is" format
        """
        After analyzing the options, the answer is C.
        Confidence: 75
        I chose this because...
        """,

        # Verbal confidence
        """
        Answer: A
        Confidence: very high
        The reasoning is...
        """,

        # Percentage format
        """
        I'm 90% confident that D is correct.
        Answer: D
        """,

        # Therefore format
        """
        The evidence points to conclusion B.
        Therefore, B is the correct answer.
        """,

        # Malformed response
        """
        Hmm, let me think about this more carefully...
        """,

        # Early answer (suspicious)
        """
        A. Let me explain why A is correct...
        ---
        Answer: A
        Confidence: 90
        ---
        """,
    ]

    print("Testing Robust Answer Parser")
    print("=" * 60)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input (first 200 chars): {test[:200]}...")

        result = parser.parse(test)
        print(f"  Answer: {result.answer}")
        print(f"  Confidence: {result.confidence}%")
        print(f"  Method: {result.extraction_method}")
        print(f"  Valid: {result.is_valid}")
        if result.warning:
            print(f"  Warning: {result.warning}")
        print(f"  Reasoning (first 100 chars): {result.reasoning[:100]}...")


if __name__ == "__main__":
    test_parser()
