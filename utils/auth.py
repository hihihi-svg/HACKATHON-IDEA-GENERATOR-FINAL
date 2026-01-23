import hashlib
from utils.db import get_db_connection, init_db

# Initialize DB on import
init_db()

def hash_password(password):
    """Simple SHA-256 hashing for hackathon MVP."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, password):
    """Verify password against stored hash."""
    return stored_hash == hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, email=""):
    """Register a new user. Returns (Success, Message)."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if user exists
    c.execute("SELECT username FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False, "Username already exists."
    
    # Create user
    pwd_hash = hash_password(password)
    try:
        c.execute(
            "INSERT INTO users (username, password_hash, email, credits_left) VALUES (?, ?, ?, ?)",
            (username, pwd_hash, email, 2)
        )
        conn.commit()
        conn.close()
        return True, "Registration successful! Us Log in."
    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"

def login_user(username, password):
    """Login user. Returns (UserObj, Message)."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user and verify_password(user['password_hash'], password):
        return dict(user), "Login successful!"
    return None, "Invalid username or password."

def get_credits(username):
    """Get current credits for a user."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT credits_left FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result['credits_left'] if result else 0

def decrement_credits(username):
    """Decrement user credits by 1."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET credits_left = credits_left - 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def create_owner_account():
    """Ensure the owner account exists with admin privileges."""
    conn = get_db_connection()
    c = conn.cursor()
    
    import os
    username = "great"
    password = os.environ.get("ADMIN_PASSWORD", "rvce")
    pwd_hash = hash_password(password)
    
    # Check if exists
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone():
        # Update existing to ensure admin rights and correct password
        c.execute("""
            UPDATE users 
            SET password_hash = ?, is_admin = 1, credits_left = 999999 
            WHERE username = ?
        """, (pwd_hash, username))
    else:
        # Create new
        c.execute("""
            INSERT INTO users (username, password_hash, email, credits_left, is_admin) 
            VALUES (?, ?, 'owner@hackathon.com', 999999, 1)
        """, (username, pwd_hash))
    
    conn.commit()
    conn.close()

# Initialize owner account on startup
create_owner_account()
