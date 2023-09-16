import json
import numpy as pd
import pandas as pd
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['hotel']
# rooms = db['hotel_screen']
# rooms = db['overnight_customer_data']
rooms = db['rest_customer_data']
# for room in rooms.find():
#     print(room)
rooms.delete_many({})
