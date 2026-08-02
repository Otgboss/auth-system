from flask import Flask, render_template, request, redirect, url_for, flash, session
from auth import create_account, authenticate_user

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        success, message = create_account(username, password)
        flash(message)
        if success:
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        success, message = authenticate_user(username, password)
        flash(message)
        if success:
            session["username"] = username
            return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/home")
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", username=session["username"])

@app.route("/logout")
def logout():
    flash("You have been logged out.")
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)