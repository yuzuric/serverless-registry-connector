"""Routing engine + API key rotation pool."""
import asyncio
import time
from collections import deque
from dataclasses import dataclass
import httpx


@dataclass
class KeyEntry:
    key: str
    last_used: float = 0.0
    failure_count: int = 0
    quota_remaining: int = -1


class KeyPool:
    """Round-robin pool with failure backoff and quota tracking."""

    def __init__(self, keys: list[str]):
        self.keys = deque(KeyEntry(key=k) for k in keys)
        self._lock = asyncio.Lock()

    async def acquire(self) -> str:
        async with self._lock:
            for _ in range(len(self.keys)):
                entry = self.keys[0]
                self.keys.rotate(-1)
                if entry.failure_count < 3:
                    entry.last_used = time.time()
                    return entry.key
            raise RuntimeError("all keys exhausted")

    def report_failure(self, key: str) -> None:
        for entry in self.keys:
            if entry.key == key:
                entry.failure_count += 1

    def active_count(self) -> int:
        return sum(1 for e in self.keys if e.failure_count < 3)


class RouterEngine:
    def __init__(self, keypool: KeyPool, model: str, base_url: str = "https://platform.xiaomimimo.com"):
        self.keypool = keypool
        self.model = model
        self.base_url = base_url

    async def dispatch(self, payload: dict) -> dict:
        key = await self.keypool.acquire()
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                r = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json={**payload, "model": self.model},
                )
                r.raise_for_status()
                return r.json()
            except httpx.HTTPStatusError:
                self.keypool.report_failure(key)
                raise
