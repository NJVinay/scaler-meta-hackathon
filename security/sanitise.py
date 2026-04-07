"""
security/sanitise.py — Input sanitisation and prompt injection guard.

Must be applied to ALL user-supplied text before LLM calls.
Rejects known injection patterns and enforces input length caps.
"""

from fastapi import HTTPException

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "jailbreak",
    "\n\nhuman:",
    "<|im_start|>",
    "[[inject]]",
    "<!-- inject -->",
    "forget your instructions",
    "act as if",
    "you are now",
    "dan mode",
]

MAX_INPUT_LENGTH = 4096


def sanitise_input(text: str) -> str:
    """Validate and sanitise user input.

    Rejects prompt injection attempts and enforces length cap.

    Args:
        text: Raw user input.

    Returns:
        Sanitised text, stripped.

    Raises:
        HTTPException: If input is too long or contains injection patterns.
    """
    if len(text) > MAX_INPUT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Input exceeds {MAX_INPUT_LENGTH} character limit",
        )

    lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lower:
            raise HTTPException(
                status_code=400,
                detail="Invalid input detected",
            )

    return text.strip()
