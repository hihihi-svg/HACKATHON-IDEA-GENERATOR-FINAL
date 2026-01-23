import sqlite3
import os

DB_NAME = "users.db"

def init_db():
    """Initialize the database with users table."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            email TEXT,
            credits_left INTEGER DEFAULT 2,
            is_admin BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
