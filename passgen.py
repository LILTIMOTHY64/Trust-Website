from werkzeug.security import generate_password_hash
import csv

def hash_password(password):
    return generate_password_hash(password)

users = [
    {"username": "admin", "password": hash_password("password")}
]

with open('uploads/users.csv', mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["username", "password"])
    writer.writeheader()
    writer.writerows(users)
