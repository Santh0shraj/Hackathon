# Client for Unbound API: submit jobs, poll status, fetch results.

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResponse:
    """Result of an LLM call."""
    response_text: str
    token_usage: dict[str, int]  # e.g. {"prompt": N, "completion": M, "total": N+M}


def _get_api_key() -> str | None:
    """Read Unbound API key from environment."""
    return os.environ.get("UNBOUND_API_KEY")


def _prepare_payload(model_name: str, prompt: str) -> dict[str, Any]:
    """Build the request body for the Unbound LLM API."""
    return {
        "model": model_name,
        "prompt": prompt,
        # Add other API-specific fields here when integrating the real API.
    }


def _call_unbound_api(payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    """
    Execute the HTTP request to the Unbound API.
    Replace this implementation with the real API call (e.g. requests.post).
    """
    # TODO: Replace with real call, e.g.:
    # response = requests.post(
    #     "https://api.unbound.../v1/...",
    #     headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    #     json=payload,
    #     timeout=60,
    # )
    # response.raise_for_status()
    # return response.json()

    # Placeholder: simulate API response.
    _ = payload, api_key
    return {
        "text": f"[Placeholder response for model={payload.get('model', '')}]",
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


def _parse_api_response(raw: dict[str, Any]) -> LLMResponse:
    """Map Unbound API response shape to LLMResponse."""
    response_text = raw.get("text", raw.get("content", "")) or ""
    usage = raw.get("usage") or {}
    token_usage = {
        "prompt": usage.get("prompt_tokens", 0),
        "completion": usage.get("completion_tokens", 0),
        "total": usage.get("total_tokens", 0),
    }
    if token_usage["total"] == 0:
        # Mock usage when API does not return it.
        token_usage = {"prompt": 0, "completion": len(response_text) // 4, "total": len(response_text) // 4}
    return LLMResponse(response_text=response_text, token_usage=token_usage)


def call_llm(model_name: str, prompt: str) -> LLMResponse:
    """
    Call the Unbound LLM with the given model and prompt.

    - Reads UNBOUND_API_KEY from environment.
    - Prepares request payload and returns response_text and token_usage.
    - Token usage is mocked when the API does not provide it.

    Returns:
        LLMResponse with response_text and token_usage.
    """
    api_key = _get_api_key()
    payload = _prepare_payload(model_name, prompt)

    if not api_key:
        # Placeholder path when no key is set; still return a valid structure.
        return LLMResponse(
            response_text=f"[Placeholder: no UNBOUND_API_KEY] model={model_name}",
            token_usage={"prompt": 0, "completion": 0, "total": 0},
        )

    raw = _call_unbound_api(payload, api_key)
    return _parse_api_response(raw)
