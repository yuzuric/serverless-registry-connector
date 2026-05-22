"""Tests for routing engine."""
import pytest
from serverless_registry_connector.gateway import KeyPool, RouterEngine


@pytest.mark.asyncio
async def test_keypool_rotation():
    pool = KeyPool(keys=["k1", "k2", "k3"])
    seen = set()
    for _ in range(3):
        seen.add(await pool.acquire())
    assert seen == {{"k1", "k2", "k3"}}


@pytest.mark.asyncio
async def test_keypool_failure_backoff():
    pool = KeyPool(keys=["k1", "k2"])
    pool.report_failure("k1")
    pool.report_failure("k1")
    pool.report_failure("k1")
    assert pool.active_count() == 1


def test_router_init():
    pool = KeyPool(keys=["k1"])
    r = RouterEngine(keypool=pool, model="mimo-7b")
    assert r.model == "mimo-7b"
