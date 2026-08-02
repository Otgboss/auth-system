from flask import Flask, render_template, request, redirect, url_for, flash, session
import hashlib
import os
import sqlite3

#this is a test feature branch
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
    return render_template("home.html")

@app.route("/logout")
def logout():
    flash("You have been logged out.")
    session.clear()
    return redirect(url_for("login"))
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
               CREATE TABLE IF NOT EXISTS users (
                   username TEXT PRIMARY KEY,
                   password TEXT,
                   salt TEXT,
                   attempts INTEGER
               )
''')
conn.commit()

def generate_salt():
    return os.urandom(8).hex()

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def create_account(username, password):
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    if result:
        return False, "Username already exists."
    salt = generate_salt()
    stored_password = hash_password(password, salt)
    cursor.execute('INSERT INTO users (username, password, salt, attempts) VALUES (?, ?, ?, ?)', (username, stored_password, salt, 0))
    conn.commit()
    return True, "Account created successfully."

def authenticate_user(username, password):
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    if result is None:
        return False, "Username not found."


    stored_password = result[1]
    stored_salt = result[2]
    attempts = result[3]

    if attempts >= 3:
        return False, "Account locked due to too many failed attempts."

    if hash_password(password, stored_salt) == stored_password:
        cursor.execute('UPDATE users SET attempts = 0 WHERE username = ?', (username,))
        conn.commit()
        return True, "Login successful."
    else:
        cursor.execute('UPDATE users SET attempts = attempts + 1 WHERE username = ?', (username,))
        conn.commit()
        return False, "Invalid password, try again."
if __name__ == "__main__":
    app.run(debug=True)