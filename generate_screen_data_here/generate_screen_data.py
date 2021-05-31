import json
import numpy as pd
import pandas as pd
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['hotel']

rooms = ['111','101','102','201','202','203','205','301','302','303','305',
'501','502','503','505','601','602','603','605']

for room in rooms:
    temp_dct = {'_id': room,
    'present': '0',
    'time_reminder': '',
    'overtime': '',
    'name': '',
    'checkin_time': '',
    'checkout_time': '',
    'etc': '',
    'color': '(0,0,0,1)'}
    db.hotel_screen.insert(temp_dct)
