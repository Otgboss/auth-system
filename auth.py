import database
import os
import hashlib

def generate_salt():
    return os.urandom(8).hex()

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def create_account(username, password):
    database.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    result = database.cursor.fetchone()
    if result:
        return False, "Username already exists."
    salt = generate_salt()
    stored_password = hash_password(password, salt)
    database.cursor.execute('INSERT INTO users (username, password, salt, attempts) VALUES (?, ?, ?, ?)', (username, stored_password, salt, 0))
    database.conn.commit()
    return True, "Account created successfully."

def authenticate_user(username, password):
    database.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    result = database.cursor.fetchone()
    if result is None:
        return False, "Username not found."


    stored_password = result[1]
    stored_salt = result[2]
    attempts = result[3]

    if attempts >= 3:
        return False, "Account locked due to too many failed attempts."

    if hash_password(password, stored_salt) == stored_password:
        database.cursor.execute('UPDATE users SET attempts = 0 WHERE username = ?', (username,))
        database.conn.commit()
        return True, "Login successful."
    else:
        database.cursor.execute('UPDATE users SET attempts = attempts + 1 WHERE username = ?', (username,))
        database.conn.commit()
        return False, "Invalid password, try again."