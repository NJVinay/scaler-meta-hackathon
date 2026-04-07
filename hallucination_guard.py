"""
hallucination_guard.py — Output validation for Gemini 3 Pro responses.

Gemini 3 Pro has an ~88% hallucination rate on misses.
Always validate structured output against expected schemas.
"""

from pydantic import BaseModel
from typing import Optional


def validate_structured_output(
    raw: str,
    schema: type[BaseModel],
) -> tuple[bool, Optional[BaseModel], str]:
    """Validate Gemini output against a Pydantic schema.

    Attempts multiple parsing strategies:
      1. Direct JSON parse
      2. Strip markdown code fences, then parse
      3. Extract JSON object from mixed text

    Returns:
        (is_valid, parsed_object_or_None, error_message)
    """
    raw = raw.strip()

    # Strategy 1: Direct parse
    try:
        obj = schema.model_validate_json(raw)
        return True, obj, ""
    except Exception:
        pass

    # Strategy 2: Strip markdown code fences
    if raw.startswith("```"):
        lines = raw.split("\n")
        # Remove first and last lines (the fences)
        inner = "\n".join(lines[1:-1]) if len(lines) > 2 else ""
        try:
            obj = schema.model_validate_json(inner)
            return True, obj, ""
        except Exception:
            pass

    # Strategy 3: Extract JSON object from mixed text
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        json_str = raw[start:end]
        obj = schema.model_validate_json(json_str)
        return True, obj, ""
    except Exception:
        pass

    # Strategy 4: Try extracting JSON array
    try:
        start = raw.index("[")
        end = raw.rindex("]") + 1
        json_str = raw[start:end]
        obj = schema.model_validate_json(json_str)
        return True, obj, ""
    except Exception as e:
        return False, None, f"Failed to parse output: {str(e)[:200]}"


def extract_text_answer(raw: str) -> str:
    """Extract a clean text answer from Gemini output.

    Strips markdown, code fences, and leading/trailing noise.
    Useful for non-JSON responses like classification labels.
    """
    text = raw.strip()

    # Strip code fences
    if text.startswith("```") and text.endswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]).strip()

    # Strip surrounding quotes
    if (text.startswith('"') and text.endswith('"')) or (
        text.startswith("'") and text.endswith("'")
    ):
        text = text[1:-1].strip()

    # Strip backticks
    text = text.strip("`")

    return text
