from werkzeug.security import generate_password_hash
import csv


# Function to hash a password using Werkzeug's generate_password_hash
def hash_password(password):
    return generate_password_hash(password)


# Sample user data with hashed password
users = [{"username": "admin", "password": hash_password("password")}]

# Write user data to a CSV file
with open("uploads/users.csv", mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["username", "password"])

    # Write header row
    writer.writeheader()

    # Write each user's data as a row in the CSV file
    writer.writerows(users)
