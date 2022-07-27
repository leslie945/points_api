from datetime import datetime, date
from typing import List, Dict

from fastapi import FastAPI, HTTPException

from utils import list_contains
from models import Database, PointRecord, SpendRequest, SpendResult

database: Database = Database()

app = FastAPI()

@app.get('/balance')
async def get_points_balance() -> Dict:
    '''
        Get points balance
        ------------------
        
        View points balance per payer or {'NO POINTS': -1}
    '''
    # sort by payer
    db = database.read_sorted(lambda x: x.payer)
    res: Dict = {}

    #loop & add up amounts
    for record in db:
        payer: str = record.payer
        amount: int = record.amount
        if payer in res:
            res[payer] += amount
        else:
            res[payer] = amount
    
    if res == {}:
        return {'NO POINTS': -1}
    else: 
        return res

@app.post('/points')
async def add_points(records: List[PointRecord]):
    '''
        Add points
        ----------
        
        Allows addition of multiple points transactions at a time, raises exception on negative balance

        Error States
        ------------
        Invalid transactions, at least one payer has a negative balance
    '''
    db = database.read()
    for record in records:
        payer: str = record.payer
        amount: int = record.amount
        timestamp: datetime = record.timestamp
        record_date: date = timestamp.date()

        #determine if database already has a record for the same payer on the same day
        item = list_contains(db, lambda x: x.payer == payer and x.timestamp.date() == record_date)
        if item is not None:
            item.amount += amount 
            if timestamp < item.timestamp:
                item.timestamp = timestamp
        else:
            db.append(record)
    item = list_contains(db, lambda x: x.amount < 0)
    if item is not None:
        raise HTTPException(status_code=400, detail='Invalid transactions, at least one payer has a negative balance' )
    database.store(db)

@app.put('/spend')
async def spend_points(spend: SpendRequest) -> List[SpendResult]:
    '''
        Spend
        -----
        
        Returns points spent per payer or raises exception.

        Exceptions
        ----------
        No points spent - requested number of points <= 0
        Too few points to spend - number of points requested > the total available across all payers
    '''
    db = database.read_sorted()
    res = []
    points: int = spend.points
    if points <= 0:
        raise HTTPException(status_code=400, detail='No points spent')
    for record in db:
        if points > 0 and record.amount > 0:
            comparison = record.amount - points
            if comparison > 0:
                res.append({'payer': record.payer, 'points': -comparison})
                points -= comparison
                record.amount -= comparison
                break
            else:
                res.append({'payer': record.payer, 'points': -record.amount })
                points -= record.amount
                record.amount = 0
        else:
            break

    if points > 0:
        raise HTTPException(status_code=400, detail='Too few points to spend')
    else:
        database.store(db)
        return res
        