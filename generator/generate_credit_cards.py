import os
import string
from faker import Faker
import csv
import random


fake = Faker()

card_types = ['visa16', 'visa19', 'mastercard', 'amex']
weights = [30, 20, 30, 20]  

credit_card_numbers = []
while len(credit_card_numbers) < 100000:
    ccn = fake.credit_card_number(card_type=random.choices(card_types, weights=weights)[0])
    if len(ccn) >= 16:
        credit_card_numbers.append(ccn)
        

def random_number_for_metadata():
    return random.randint(100,800)

# Generate two random numbers of 16 to 19 digits
def generate_random_number():
    return ''.join(random.choice(string.digits) for _ in range(random.randint(16, 19)))

with open('/home/elion/metadata.txt','w') as f:
    writer = csv.writer(f)
    offset = random_number_for_metadata()
    writer.writerow([offset])
    writer.writerow([])
    for number in credit_card_numbers:
        writer.writerow([len(number)])

file_path = '/home/elion/credit_card_numbers.txt' 

with open(file_path, 'w', newline='') as file:
    writer = csv.writer(file)
    for number in credit_card_numbers:
        random_number1 = generate_random_number()
        random_number2 = generate_random_number()
        
        characters = string.ascii_letters + string.digits
        random_ints_debut = ''.join(random.choice(characters) for _ in range(offset - len(random_number1)))
        insert_position_debut = random.randint(0, len(random_ints_debut))
        random_ints_debut = random_ints_debut[:insert_position_debut] + random_number1 + random_ints_debut[insert_position_debut:]
        
        remaining_length = 900 - offset - len(random_number2)
        random_ints_fin = ''.join(random.choice(characters) for _ in range(remaining_length - len(random_number2)))
        insert_position_fin = random.randint(0, len(random_ints_fin))
        
        random_ints_fin = random_ints_fin[:insert_position_fin] + random_number2 + random_ints_fin[insert_position_fin:]
        
        hidden_pan = str(random_ints_debut) + str(number) + str(random_ints_fin)
        writer.writerow([hidden_pan])
        
with open('/home/elion/credit_card_numbers_fr.txt', 'w', newline='') as file:
    writer = csv.writer(file)
    for number in credit_card_numbers:
        writer.writerow([number])

print("File created at:", file_path) 