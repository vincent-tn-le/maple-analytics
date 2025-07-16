"""Run hourly.  Pull SEA ranking API → DB rows (Level ≥261)"""
import asyncio, json, os, datetime as dt
from typing import List

import aiohttp
from sqlalchemy.exc import IntegrityError

from db import Session, RankSnapshot, init_db
from token import get_token

# MapleSEA world IDs as per OpenAPI doc (Apr 2025)
WORLDS = {
    "Aquila": 0,
    "Bootes": 1,
    "Cassiopeia": 2,
    "Delphinus": 3,
    "Eridanus": 4
}
BASE_URL = "https://openapi.nexon.com/game/maplestorysea/v1/ranking/character"

async def fetch_world(sess: aiohttp.ClientSession, world_name: str, world_id: int) -> List[dict]:
    token = await get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "x-nxopenapi-key": os.getenv("MSEA_APP_ID"),
        "accept": "application/json",
    }
    params = {
        "type": "overall",
        "world_id": world_id,
        "date": dt.date.today().isoformat(),  # today snapshot
        "limit": 1000,  # max allowed per OpenAPI; adjust pagination if >1k
        "offset": 0,
    }
    rows: list[dict] = []
    while True:
        async with sess.get(BASE_URL, headers=headers, params=params) as r:
            if r.status != 200:
                print("Error", r.status, await r.text()); break
            payload = await r.json()
        chunk = payload.get("ranking", [])
        rows.extend(chunk)
        if len(chunk) < params["limit"]:  # last page
            break
        params["offset"] += params["limit"]
    # filter L≥261 early
    return [row for row in rows if row["level"] >= 261]

async def main():
    init_db()
    ts = dt.datetime.utcnow()
    async with aiohttp.ClientSession() as sess, Session() as db:
        for name, wid in WORLDS.items():
            try:
                records = await fetch_world(sess, name, wid)
            except Exception as e:
                print(f"{name}: fetch error", e); continue
            for row in records:
                snap = RankSnapshot(
                    world_id=wid,
                    character_id=row["character_id"],
                    name=row["character_name"],
                    job_id=row["job_id"],
                    level=row["level"],
                    rank=row["ranking"],
                    exp=row["experience"],
                    snapshot_ts=ts,
                )
                db.add(snap)
            try:
                db.commit()
                print(f"{name}: inserted {len(records)} rows")
            except IntegrityError:
                db.rollback()
                print(f"{name}: duplicate rows skipped")

if __name__ == "__main__":
    asyncio.run(main())