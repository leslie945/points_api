from datetime import datetime
from typing import List

from pydantic import BaseModel

class SpendRequest(BaseModel):
    points: int

class SpendResult(BaseModel):
    payer: str
    amount: int

class PointRecord(BaseModel): 
    payer: str
    amount: int
    timestamp: datetime
    
    #timestamp equivalency for list sort
    def __eq__(self, other) -> bool:
        return self.timestamp == other.timestamp
    
    #oldest timestamp non-zero points
    def __gt__(self, other) -> bool:
        return self.timestamp > other.timestamp and self.amount != 0

    #newest timstamp non-zero points
    def __lt__(self, other) -> bool:
        return self.timestamp < other.timestamp and self.amount != 0

class Database():
    _db: List[PointRecord]

    def __init__(self):
        self._db = []

    def read(self):
        return self._db.copy()

    def store(self, db):
        self._db = db

    def read_sorted(self):
        return sorted(self._db)
