"""
FastAPI gateway routing requests to Xiaomi MiMo with key rotation + rate limits.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from serverless_registry_connector.gateway import RouterEngine, KeyPool
from serverless_registry_connector.config import load_config

app = FastAPI(title="MiMo API Gateway")
config = load_config("config.yaml")
keypool = KeyPool(config["api_keys"])
router = RouterEngine(keypool=keypool, model=config["model"])


class ChatRequest(BaseModel):
    messages: list[dict]
    temperature: float = 0.7
    max_tokens: int = 512


@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    try:
        return await router.dispatch(req.dict())
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/health")
async def health():
    return {{"status": "ok", "active_keys": keypool.active_count()}}
