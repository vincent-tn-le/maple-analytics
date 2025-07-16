"""Compute end‑of‑day EXP gain per character."""
import datetime as dt
from sqlalchemy import select, func, update
from db import Session, RankSnapshot, EndOfDayExp, init_db

init_db()

today = dt.date.today()
yday = today - dt.timedelta(days=1)
start = dt.datetime.combine(yday, dt.time.min)
end   = dt.datetime.combine(yday, dt.time.max)

with Session() as db:
    # For each character, find first & last snapshot EXP on yday
    subq = (
        select(
            RankSnapshot.character_id.label("cid"),
            func.min(RankSnapshot.exp).label("exp_start"),
            func.max(RankSnapshot.exp).label("exp_end"),
        )
        .where(RankSnapshot.snapshot_ts.between(start, end))
        .group_by(RankSnapshot.character_id)
    ).subquery()

    results = db.execute(select(subq.c.cid,
                                subq.c.exp_end,
                                (subq.c.exp_end - subq.c.exp_start).label("gain")))

    for cid, exp_end, gain in results:
        row = EndOfDayExp(character_id=cid,
                          day=yday,
                          exp_end=exp_end,
                          exp_gain=gain)
        db.merge(row)  # upsert
    db.commit()
    print("EOD job complete ✔")
