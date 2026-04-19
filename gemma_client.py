"""
gemma_client.py — Gemma 4 client via OpenAI-compatible SDK.

Uses environment variables only — never hardcoded credentials.
Supports thinking_config with configurable thinking_level.
"""

import os
from openai import OpenAI


def build_client() -> OpenAI:
    """Build an OpenAI-compatible client for Gemma 4.

    Reads credentials from environment variables:
      - HF_TOKEN or API_KEY → api_key
      - API_BASE_URL → base_url

    Raises:
        EnvironmentError: If required env vars are missing.
    """
    api_key = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
    base_url = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")

    if not api_key:
        raise EnvironmentError(
            "HF_TOKEN or API_KEY must be set. See .env.example for required variables."
        )
    if not base_url:
        raise EnvironmentError("API_BASE_URL must be set.")

    return OpenAI(base_url=base_url, api_key=api_key)


def call_gemma(
    client: OpenAI,
    prompt: str,
    system: str = "",
    thinking_level: str = "dynamic",
    max_tokens: int = 2048,
    temperature: float = 0.7,
) -> str:
    """Call Gemma 4 with thinking_config support.

    Args:
        client:          OpenAI client instance.
        prompt:          User prompt text.
        system:          Optional system prompt.
        thinking_level:  "low", "high", or "dynamic" (default).
        max_tokens:      Max response tokens.
        temperature:     Sampling temperature.

    Returns:
        The model's response text, stripped.
    """
    model = os.getenv("MODEL_NAME", "google/gemma-4-31B-it")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={"thinking_config": {"thinking_level": thinking_level}},
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        # Fallback: try without thinking_config for compatibility
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception:
            raise e  # Re-raise original error
