import copy

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

    #used for test comparison
    def __hash__(self):
        return hash(tuple(self))
    
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
        return copy.deepcopy(self._db)

    def store(self, db):
        self._db = db

    def read_sorted(self, key=None):
        return sorted(self.read(), key=key)
