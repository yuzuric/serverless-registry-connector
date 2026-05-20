"""Lightweight async client for the Xiaomi MiMo OpenAI-compatible API."""
import logging
from typing import Any
import httpx

logger = logging.getLogger(__name__)


class MiMoClient:
    DEFAULT_BASE = "https://platform.xiaomimimo.com/v1"

    def __init__(self, model: str, api_key: str, base_url: str | None = None, timeout: float = 60.0):
        self.model = model
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE).rstrip("/")
        self.timeout = timeout

    async def chat(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {}),
            }

    def chat_sync(self, prompt: str, max_tokens: int = 512) -> str:
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                },
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
