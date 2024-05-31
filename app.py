from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename
import os
import csv

app = Flask(__name__)
app.secret_key = "your_secret_key"

UPLOAD_FOLDER = r"uploads/IDs"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

data_file = r"uploads/requests.csv"

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def load_requests():
    requests = []
    try:
        with open(data_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                requests.append(row)
    except FileNotFoundError:
        pass
    return requests


def save_requests(requests):
    with open(data_file, mode="w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["id", "name", "email", "school", "program", "details", "identity_proof"],
        )
        writer.writeheader()
        writer.writerows(requests)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        school = request.form['school']
        program = request.form['program']
        details = request.form['details']

        # Load existing requests to determine the new request ID
        requests = load_requests()
        new_id = len(requests) + 1

        # Get the uploaded file
        if 'identity_proof' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['identity_proof']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file:
            # Rename the file to the request ID before saving
            filename = secure_filename(f"{new_id}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Save form data to the CSV file
            new_request = {
                "id": new_id,
                "name": name,
                "email": email,
                "school": school,
                "program": program,
                "details": details,
                "identity_proof": file_path
            }
            requests.append(new_request)
            save_requests(requests)

            flash('Request submitted successfully', 'success')
            return redirect(url_for('index'))

    return render_template('submit.html')


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "password":
            return redirect(url_for("requests"))
        else:
            flash("Invalid credentials", "error")  # Flash error message
            return redirect(url_for("admin_login"))
    return render_template("admin_login.html")


@app.route("/requests")
def requests():
    requests = load_requests()
    return render_template("requests.html", requests=requests)


@app.route("/donate")
def donate():
    return render_template("donate.html")


if __name__ == "__main__":
    app.run(debug=True)
