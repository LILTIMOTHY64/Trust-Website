from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    flash,
    session,
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import csv
from functools import wraps

# Initialize Flask application
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Define upload folder paths
REQUEST_UPLOAD_FOLDER = r"uploads/REQ_IDs"
app.config["REQUEST_UPLOAD_FOLDER"] = REQUEST_UPLOAD_FOLDER

VOLUNTEER_UPLOAD_FOLDER = r"uploads/VOL_IDs"
app.config["VOLUNTEER_UPLOAD_FOLDER"] = VOLUNTEER_UPLOAD_FOLDER

CSV_FOLDER = r"uploads"
app.config["CSV_FOLDER"] = CSV_FOLDER

# Define CSV file paths for requests,volunteers and users
data_file = r"uploads/requests.csv"
volunteer_file = r"uploads/volunteer.csv"
users_file = r"uploads/users.csv"

# Ensure the upload directories exist
os.makedirs(REQUEST_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VOLUNTEER_UPLOAD_FOLDER, exist_ok=True)

# Function to load help requests from CSV file
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

# Function to save help requests to CSV file
def save_requests(requests):
    with open(data_file, mode="w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "name",
                "email",
                "number",
                "school",
                "year",
                "purpose",
                "details",
                "identity_proof",
            ],
        )
        writer.writeheader()
        writer.writerows(requests)

# Function to load volunteer information from CSV file
def load_volunteers():
    volunteers = []
    try:
        with open(volunteer_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                volunteers.append(row)
    except FileNotFoundError:
        pass
    return volunteers

# Function to save volunteer information to CSV file
def save_volunteers(volunteers):
    with open(volunteer_file, mode="w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "name",
                "email",
                "phone",
                "address",
                "specialization",
                "identity_proof",
            ],
        )
        writer.writeheader()
        writer.writerows(volunteers)

def load_users():
    users = []
    try:
        with open(users_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(row)
    except FileNotFoundError:
        pass
    return users

def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_logged_in" not in session or not session["admin_logged_in"]:
            flash("You must be logged in to access this page", "error")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

# Route for home page
@app.route("/")
def index():
    return render_template("index.html")

# Route for submitting a help request
@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        email = request.form["email"]
        number = request.form["number"]
        school = request.form["school"]
        year = request.form["year"]
        purpose = request.form["purpose"]
        details = request.form["details"]

        # Load existing requests to determine the new request ID
        requests = load_requests()
        new_id = len(requests) + 1

        # Handle file upload
        if "identity_proof" not in request.files:
            flash("No file part", "error")
            return redirect(request.url)
        file = request.files["identity_proof"]
        if file.filename == "":
            flash("No selected file", "error")
            return redirect(request.url)
        if file:
            # Save the uploaded file
            file_ext = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"{name}_{new_id}{file_ext}")  # Ensure unique filename
            file_path = os.path.join(app.config["REQUEST_UPLOAD_FOLDER"], filename)
            file.save(file_path)

            # Save form data to the CSV file
            new_request = {
                "id": new_id,
                "name": name,
                "email": email,
                "number": number,
                "school": school,
                "year": year,
                "purpose": purpose,
                "details": details,
                "identity_proof": filename,
            }
            requests.append(new_request)
            save_requests(requests)

            flash("Request submitted successfully", "success")
    return render_template("submit.html")

# Route for admin login
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        users = load_users()
        user = next((u for u in users if u["username"] == username), None)

        if user and verify_password(user["password"], password):
            session["admin_logged_in"] = True
            requests = load_requests()
            volunteers = load_volunteers()
            return render_template("admin.html", requests=requests, volunteers=volunteers)
        else:
            flash("Invalid credentials", "error")
            return redirect(url_for("admin_login"))

    return render_template("admin_login.html")

# Route for admin page with login required
'''@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    requests = load_requests()
    volunteers = load_volunteers()
    return render_template("admin.html", requests=requests, volunteers=volunteers)
'''
# Route for downloading requests CSV with login required
@app.route("/admin/download-requests")
@login_required
def admin_download_requests():
    return send_from_directory(app.config["CSV_FOLDER"], "requests.csv", as_attachment=True)

# Route for downloading volunteers CSV with login required
@app.route("/admin/download-volunteers")
@login_required
def admin_download_volunteers():
    return send_from_directory(app.config["CSV_FOLDER"], "volunteer.csv", as_attachment=True)

@app.route('/uploads/REQ_IDs/<filename>')
def uploaded_request_file(filename):
    return send_from_directory(app.config['REQUEST_UPLOAD_FOLDER'], filename)

@app.route('/uploads/VOL_IDs/<filename>')
def uploaded_volunteer_file(filename):
    return send_from_directory(app.config['VOLUNTEER_UPLOAD_FOLDER'], filename)

# Route for donation page
@app.route("/donate")
def donate():
    return render_template("donate.html")

# Route for gallery page
@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

# Route for volunteer registration
@app.route("/volunteer", methods=["GET", "POST"])
def volunteer():
    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        specialization = request.form["specialization"]

        # Handle file upload
        if "identity_proof" not in request.files:
            flash("No file part", "error")
            return redirect(request.url)
        file = request.files["identity_proof"]
        if file.filename == "":
            flash("No selected file", "error")
            return redirect(request.url)
        if file:
            # Save the uploaded file
            file_ext = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"{name}_{file_ext}")  # Ensure unique filename
            file_path = os.path.join(app.config["VOLUNTEER_UPLOAD_FOLDER"], filename)
            file.save(file_path)

        # Load existing volunteers
        volunteers = load_volunteers()

        # Save form data to the CSV file
        new_volunteer = {
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "specialization": specialization,
            "identity_proof": filename,
        }
        volunteers.append(new_volunteer)
        save_volunteers(volunteers)

        flash("Volunteer information submitted successfully", "success")

    return render_template("volunteer.html")

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
