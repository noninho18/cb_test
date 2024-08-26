import json
import random
import time
from datetime import datetime
from hdfs import InsecureClient
from faker import Faker

# Use the actual IP address of the NameNode
hdfs_url = 'http://172.20.0.2:50070'
hdfs_client = InsecureClient(hdfs_url, user='root')

output_dir = "/transactions/"

fake = Faker()

card_types = ['visa16', 'visa19', 'mastercard', 'amex']
weights = [30, 20, 30, 20]  

def generate_transaction():
    return {
        "user_id": random.randint(1000, 9999),
        "transaction_amount": round(random.uniform(1.0, 1000.0), 2),
        "card": fake.credit_card_number(card_type=random.choices(card_types, weights=weights)[0]),
        "timestamp": int(time.time()),
        "merchant_id": random.randint(100, 999)
    }

while True:
    transactions = []
    for _ in range(10000):
        transactions.append(generate_transaction())

    filename = f"transaction_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.json"
    file_path = output_dir + filename

    try:
        with hdfs_client.write(file_path, encoding='utf-8') as writer:
            json.dump(transactions, writer)
        print(f"Generated and stored 10000 transactions in: {file_path}")
    except Exception as e:
        print(f"Failed to write to HDFS: {e}")
        
    time.sleep(60)