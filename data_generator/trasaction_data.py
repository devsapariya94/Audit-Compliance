import random
import pandas as pd
from datetime import datetime, timedelta
import uuid
from pymongo import MongoClient

# Constants
num_users = 10
num_transactions = 100
modes = ['UPI', 'Net Banking', 'Credit Card', 'Debit Card', 'Wallet']

# Generate random data
data = []
for _ in range(num_transactions):
    sender_id = random.randint(1, num_users)
    receiver_id = random.randint(1, num_users)
    while receiver_id == sender_id:
        receiver_id = random.randint(1, num_users)
    
    transaction_id = str(uuid.uuid4())
    mode = random.choice(modes)
    time = datetime.now() - timedelta(days=random.randint(0, 365))
    amount = round(random.uniform(10.0, 1000.0), 2)
    
    data.append({
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'transaction_id': transaction_id,
        'mode': mode,
        'time': time,
        'amount': amount
    })

# Convert to DataFrame
df = pd.DataFrame(data)
print(df)

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['bank_database']
collection = db['transactions']

# Convert DataFrame to list of dictionaries
data_dict = df.to_dict('records')

# Insert data into MongoDB
collection.insert_many(data_dict)

print("Data inserted successfully!")
