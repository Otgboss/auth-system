import database
import unittest
import sqlite3
from auth import create_account, authenticate_user

class TestAuth(unittest.TestCase):
    def setUp(self):
        database.conn = sqlite3.connect(":memory:")
        database.cursor = database.conn.cursor()
        database.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,
            password TEXT,
            salt TEXT,
            attempts INTEGER
            )
        ''')
        database.conn.commit()

    def tearDown(self):
        database.conn.close()

    def test_create_account_success(self):
        success, message = create_account("testuser", "password123")
        self.assertTrue(success)
        self.assertEqual(message, "Account created successfully.")
    def test_create_account_duplicate(self):
        create_account("testuser", "password123")
        success, message = create_account("testuser", "password123")
        self.assertFalse(success)
        self.assertEqual(message, "Username already exists.")
    def test_login_success(self):
        create_account("testuser", "password123")
        success, message = authenticate_user("testuser", "password123")
        self.assertTrue(success)
    def test_login_wrong_password(self):
        create_account("testuser", "password123")
        success, message = authenticate_user("testuser", "wrongpassword")
        self.assertFalse(success)
    def test_account_locked(self):
        create_account("testuser", "password123")
        authenticate_user("testuser", "wrongpassword")
        authenticate_user("testuser", "wrongpassword")
        authenticate_user("testuser", "wrongpassword")
        success, message = authenticate_user("testuser", "password123")
        self.assertFalse(success)
        self.assertEqual(message, "Account locked due to too many failed attempts.")