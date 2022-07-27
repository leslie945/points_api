import unittest
import copy

from time import strptime
from datetime import datetime
from typing import List, Dict

from fastapi.testclient import TestClient

from custom_assertions import CustomAssertions

import sys
from pathlib import Path
sys.path[0] = str(Path(sys.path[0]).parent)

from models import PointRecord
from main import app, database
from utils import list_contains


class TestMain(unittest.TestCase, CustomAssertions):
    def setUp(self):
        database.store([])
        self.dt_format = '%Y-%m-%d %H %z'
        self.client = TestClient(app)

    def test_add_good_input(self):
        good_input: List[Dict] = [
                {'payer': 'A' ,'amount': 1, 'timestamp': '2020-04-15T15:00:00.000Z'},
                {'payer': 'B' ,'amount': 1, 'timestamp': '2020-04-15T20:00:00.000Z'},
                {'payer': 'A' ,'amount': 1, 'timestamp': '2020-04-15T10:00:00.000Z'},
                {'payer': 'B' ,'amount': 5, 'timestamp': '2020-04-15T21:00:00.000Z'},
                {'payer': 'C' ,'amount': 3, 'timestamp': '2020-04-16T09:00:00.000Z'},
            ]
        response = self.client.post(
            '/points',
            json=good_input
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json())
        
        db = database.read()
        itemA = list_contains(db, lambda x : x.payer == 'A')
        self.assertIsNotNone(itemA)
        self.assertEqual(itemA.amount, 2)
        self.assertEqual(itemA.timestamp, datetime.strptime('2020-04-15 10 +0000', self.dt_format))

        itemB = list_contains(db, lambda x: x.payer == 'B')
        self.assertIsNotNone(itemB)
        self.assertEqual(itemB.amount, 6)
        self.assertEqual(itemB.timestamp, datetime.strptime('2020-04-15 20 +0000', self.dt_format))

        itemC = list_contains(db, lambda x: x.payer == 'C')
        self.assertIsNotNone(itemC)
        self.assertEqual(itemC.amount, 3)
        self.assertEqual(itemC.timestamp, datetime.strptime('2020-04-16 09 +0000', self.dt_format))

        noItem = list_contains(db, lambda x: x.payer == 'D')
        self.assertIsNone(noItem)

    def test_add_bad_input(self):
        bad_input: List[Dict] = [
            {'payer': 'A' ,'amount': 1, 'timestamp': '2020-04-15T15:00:00.000Z'},
            {'payer': 'B' ,'amount': 1, 'timestamp': '2020-04-15T20:00:00.000Z'},
            {'payer': 'A' ,'amount': -3, 'timestamp': '2020-04-15T10:00:00.000Z'},
            {'payer': 'B' ,'amount': 1, 'timestamp': '2020-04-15T21:00:00.000Z'},
            {'payer': 'C' ,'amount': 1, 'timestamp': '2020-04-16T09:00:00.000Z'},
        ]
        
        response = self.client.post(
            '/points',
            json=bad_input
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Invalid transactions, at least one payer has a negative balance'})
        self.assertEqual(len(database.read()), 0)

        good_input: List[Dict] = [
            {'payer': 'A' ,'amount': 1, 'timestamp': '2020-04-15T15:00:00.000Z'},
            {'payer': 'B' ,'amount': 1, 'timestamp': '2020-04-15T20:00:00.000Z'}
        ]

        bad_input = [
            {'payer': 'A' ,'amount': -3, 'timestamp': '2020-04-15T10:00:00.000Z'},
            {'payer': 'B' ,'amount': 1, 'timestamp': '2020-04-15T21:00:00.000Z'},
            {'payer': 'C' ,'amount': 1, 'timestamp': '2020-04-16T09:00:00.000Z'},
        ]

        response = self.client.post(
            '/points',
            json=good_input
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(database.read()), 2)

        before_changes = copy.deepcopy(database.read())

        response = self.client.post(
            '/points',
            json=bad_input
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Invalid transactions, at least one payer has a negative balance'})
        self.assertEqual(len(database.read()), 2)
        self.assertSamePointRecords(database.read(), before_changes)


    def test_spend_points_good_input(self):
        original: List[PointRecord] = [
            PointRecord(payer='A' , amount=1, timestamp=datetime.strptime('2020-04-10 15 +0000', self.dt_format)),
            PointRecord(payer='B' , amount=2, timestamp=datetime.strptime('2020-04-15 20 +0000', self.dt_format)),
            PointRecord(payer='C' , amount=3, timestamp=datetime.strptime('2020-04-16 09 +0000', self.dt_format)),
            PointRecord(payer='D' , amount=1, timestamp=datetime.strptime('2020-04-15 10 +0000', self.dt_format)),
        ]

        database.store(copy.deepcopy(original))

        response = self.client.put(
            '/spend',
            json={'points':3}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
            {'payer':'A', 'points':-1}, 
            {'payer':'D', 'points': -1}, 
            {'payer': 'B', 'points': -1}
        ])

        db = database.read()
        self.assertNotSamePointRecords(db, original)

        itemA = list_contains(db, lambda x: x.payer == 'A')
        self.assertIsNotNone(itemA)
        self.assertEqual(itemA.amount, 0)

        itemB = list_contains(db, lambda x: x.payer == 'B')
        self.assertIsNotNone(itemB)
        self.assertEqual(itemB.amount, 1)

        itemC = list_contains(db, lambda x: x.payer == 'C')
        self.assertIsNotNone(itemC)
        self.assertEqual(itemC.amount, 3)

        itemD = list_contains(db, lambda x: x.payer == 'D')
        self.assertIsNotNone(itemD)
        self.assertEqual(itemD.amount, 0)

    def test_spend_points_bad_input(self):
        response = self.client.put(
            '/spend',
            json={'points':2}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Too few points to spend'})
        
        original: List[PointRecord] = [
            PointRecord(payer='A' , amount=1, timestamp=datetime.strptime('2020-04-10 15 +0000', self.dt_format)),
            PointRecord(payer='B' , amount=1, timestamp=datetime.strptime('2020-04-15 20 +0000', self.dt_format)),
            PointRecord(payer='C' , amount=3, timestamp=datetime.strptime('2020-04-16 09 +0000', self.dt_format)),
            PointRecord(payer='D' , amount=1, timestamp=datetime.strptime('2020-04-15 10 +0000', self.dt_format)),
        ]
        
        database.store(copy.deepcopy(original))
        
        response = self.client.put(
            '/spend',
            json={'points':0}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'No points spent'})
        self.assertSamePointRecords(database.read(), original)

        response = self.client.put(
            '/spend',
            json={'points':-10}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'No points spent'})
        self.assertSamePointRecords(database.read(), original)

        response = self.client.put(
            '/spend',
            json={'points':7}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Too few points to spend'})
        self.assertSamePointRecords(database.read(), original)

    def test_get_points_balance_has_balance(self):
        original: List[PointRecord] = [
            PointRecord(payer='A' , amount=1, timestamp=datetime.strptime('2020-04-10 15 +0000', self.dt_format)),
            PointRecord(payer='B' , amount=1, timestamp=datetime.strptime('2020-04-15 20 +0000', self.dt_format)),
            PointRecord(payer='C' , amount=3, timestamp=datetime.strptime('2020-04-16 09 +0000', self.dt_format)),
            PointRecord(payer='A' , amount=1, timestamp=datetime.strptime('2020-04-15 10 +0000', self.dt_format)),
        ]

        database.store(copy.deepcopy(original))
        
        response = self.client.get('/balance')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'A': 2, 'B': 1, 'C': 3})
        self.assertSamePointRecords(database.read(), original)

    def test_get_points_balance_no_balance(self):
        response = self.client.get('/balance')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'NO POINTS': -1})

if __name__ == "__main__":
     unittest.main()
        

