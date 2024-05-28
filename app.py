from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import csv

app = Flask(__name__)
app.secret_key = "your_secret_key"

data_file = "requests.csv"


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
            fieldnames=["id", "name", "email", "school/college", "program", "details"],
        )
        writer.writeheader()
        writer.writerows(requests)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        new_request = {
            "id": str(len(load_requests()) + 1),
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "school/college": request.form.get("school/college"),
            "program": request.form.get("program"),
            "details": request.form.get("details"),
        }
        requests = load_requests()
        requests.append(new_request)
        save_requests(requests)
        flash("Request submitted successfully!", "success")  # Flash success message
        return redirect(url_for("index"))
    return render_template("submit.html")


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
