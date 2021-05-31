import json
import numpy as pd
import pandas as pd
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['hotel']
customer_data = db['customer_data']

# temp = {}
# temp['room'] = ''
# temp['name'] = ''
# temp['id'] = ''
# temp['dob'] = ''
# temp['etc'] = ''
# temp['phone_number'] = ''
# temp['email'] = ''
# temp['price'] = ''
# temp['checkInDate'] = ''
# temp['checkOutDate'] = ''
# temp['rest_or_overnight'] = ''

db.customer_data.rename('overnight_customer_data')
