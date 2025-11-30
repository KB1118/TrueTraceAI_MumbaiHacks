"""
Async client for interacting with Ollama (local REST API or OpenAI-compatible gateway).
"""
import httpx
from typing import List, Dict, Optional
from app.config import settings


class OllamaAPIError(Exception):
    """Custom exception for Ollama API failures."""


async def call_ollama_chat(
    prompt: str,
    *,
    system: str = "You are a helpful assistant.",
    temperature: float = 0.7,
    max_retries: int = 2
) -> str:
    """
    Call Ollama (local /api/chat) or an OpenAI-compatible gateway and return the response text.
    """
    base_url = settings.OLLAMA_API_BASE_URL.rstrip("/")
    uses_openai_gateway = (
        bool(settings.OLLAMA_API_KEY)
        or base_url.endswith("/v1")
        or "/v1/" in base_url
        or "api.ollama.com" in base_url
    )

    if uses_openai_gateway:
        url = f"{base_url}/chat/completions" if base_url.endswith("/v1") else f"{base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if settings.OLLAMA_API_KEY:
            headers["Authorization"] = f"Bearer {settings.OLLAMA_API_KEY}"

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]

        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": messages,
            "temperature": temperature,
        }
    else:
        url = f"{base_url}/api/chat"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": temperature},
        }

    last_error: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                if uses_openai_gateway:
                    choices = data.get("choices")
                    if not choices:
                        raise OllamaAPIError("No choices returned from Ollama API.")
                    return choices[0]["message"]["content"].strip()

                # Local Ollama format
                message = data.get("message") or {}
                content = message.get("content") or data.get("response")
                if not content:
                    raise OllamaAPIError("No content returned from Ollama local API.")
                return content.strip()
        except Exception as exc:
            last_error = exc

    raise OllamaAPIError(f"Ollama API call failed after retries: {last_error}")

