"""Fetch & cache Nexon OpenAPI bearer token (client‑credentials flow)."""
import aiohttp, asyncio, os, time

APP_ID     = os.getenv("MSEA_APP_ID")
APP_SECRET = os.getenv("MSEA_APP_SECRET")
TOKEN_URL  = "https://openapi.nexon.com/auth/token"
_cache: dict[str, tuple[str, float]] = {}

async def get_token() -> str:
    now = time.time()
    if (token_data := _cache.get("token")) and token_data[1] > now + 60:
        return token_data[0]

    async with aiohttp.ClientSession() as sess:
        payload = {"grant_type": "client_credentials",
                   "client_id": APP_ID,
                   "client_secret": APP_SECRET}
        async with sess.post(TOKEN_URL, data=payload) as resp:
            data = await resp.json()
            token = data["access_token"]
            ttl   = int(data.get("expires_in", 3600))
            _cache["token"] = (token, now + ttl)
            return token