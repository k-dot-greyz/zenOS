"""
Security framework for zenOS - defense against prompt injection and other attacks.
"""

import re
from typing import Any, Dict, List, Optional


class SecurityFramework:
    """
    Security framework for protecting against prompt injection and other attacks.
    """

    # Common injection patterns
    INJECTION_PATTERNS = [
        r"ignore.*previous.*instructions",
        r"disregard.*above",
        r"forget.*everything",
        r"new.*instructions.*follow",
        r"system.*prompt.*is",
        r"you.*are.*now",
        r"</system>",
        r"<system>",
        r"\[INST\]",
        r"###.*[Ii]nstruction",
    ]

    def __init__(self):
        """Initialize the security framework."""
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]

    def scan_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze a prompt for potential injection patterns and excessive length.
        
        Parameters:
            prompt (str): The prompt text to analyze.
        
        Returns:
            Dict[str, Any]: A security analysis containing `safe`, `risk_level`, and
                `issues` fields. `safe` is `True` when no issues are found;
                `risk_level` is `low`, `medium`, or `high`; and `issues` lists
                detected security concerns.
        """
        issues = []
        risk_level = "low"

        # Check for injection patterns
        for pattern in self.compiled_patterns:
            if pattern.search(prompt):
                issues.append(
                    {"type": "potential_injection", "pattern": pattern.pattern, "severity": "high"}
                )
                risk_level = "high"

        # Check for suspicious length
        if len(prompt) > 10000:
            issues.append({"type": "excessive_length", "severity": "medium"})
            if risk_level == "low":
                risk_level = "medium"

        return {"safe": len(issues) == 0, "risk_level": risk_level, "issues": issues}

    def sanitize_prompt(self, prompt: str) -> str:
        """
        Remove detected prompt-injection content and limit the result to 10,000 characters.
        
        Parameters:
            prompt (str): The prompt to sanitize.
        
        Returns:
            str: The sanitized prompt, with detected content replaced by "[REMOVED]" and longer results truncated.
        """
        sanitized = prompt

        # Remove potential injection attempts
        for pattern in self.compiled_patterns:
            sanitized = pattern.sub("[REMOVED]", sanitized)

        # Truncate if too long
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000] + "... [TRUNCATED]"

        return sanitized

    def validate_response(self, response: str) -> bool:
        """
        Check an AI response for common sensitive data patterns.
        
        Returns:
            bool: `True` if no email address, SSN, or 16-digit numeric sequence is found; `False` otherwise.
        """
        # Check for sensitive information patterns
        sensitive_patterns = [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{16}\b",  # Credit card
        ]

        for pattern in sensitive_patterns:
            if re.search(pattern, response):
                return False

        return True
