from datetime import datetime
import os

from sqlalchemy import (BigInteger, Column, DateTime, Integer, String,
                        create_engine, func)
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = os.getenv("DATABASE_URL", "sqlite:///maple.db")
engine = create_engine(DB_URL, future=True)
Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

class RankSnapshot(Base):
    __tablename__ = "rank_snapshots"
    id            = Column(Integer, primary_key=True)
    region        = Column(String(8),   default="MSEA", index=True)  # GMS vs MSEA
    world_id      = Column(Integer,     index=True)   # e.g. 0 = Aquila
    character_id  = Column(String(20),  index=True)
    name          = Column(String(48))
    job_id        = Column(Integer)
    level         = Column(Integer)
    rank          = Column(Integer)
    exp           = Column(BigInteger)
    snapshot_ts   = Column(DateTime,    default=datetime.utcnow, index=True)

class EndOfDayExp(Base):
    __tablename__ = "end_of_day_exp"
    id           = Column(Integer, primary_key=True)
    character_id = Column(String(20), index=True)
    day          = Column(DateTime, index=True)        # date @ 00:00 UTC
    exp_end      = Column(BigInteger)
    exp_gain     = Column(BigInteger)

def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(engine)