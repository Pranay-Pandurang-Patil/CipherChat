import sqlite3
import hashlib
import os
from datetime import datetime


# Location of our SQLite database.
DATABASE = "database/cipherchat.db"


def create_database():

    # Connect to SQLite.
    connection = sqlite3.connect(DATABASE)

    # Cursor lets us execute SQL commands.
    cursor = connection.cursor()


    # -------------------------
    # USERS
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)


    # -------------------------
    # ROOMS
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code TEXT UNIQUE NOT NULL,
            room_name TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            room_type TEXT NOT NULL,
            created_at TEXT NOT NULL,

            FOREIGN KEY (owner_id)
            REFERENCES users(id)
        )
    """)


    # -------------------------
    # ROOM MEMBERS
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS room_members (
            room_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,

            PRIMARY KEY (room_id, user_id),

            FOREIGN KEY (room_id)
            REFERENCES rooms(id),

            FOREIGN KEY (user_id)
            REFERENCES users(id)
        )
    """)


    # -------------------------
    # MESSAGES
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER,
            room_id INTEGER,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,

            FOREIGN KEY (sender_id)
            REFERENCES users(id),

            FOREIGN KEY (receiver_id)
            REFERENCES users(id),

            FOREIGN KEY (room_id)
            REFERENCES rooms(id)
        )
    """)


    # Save changes.
    connection.commit()

    # Close database.
    connection.close()


# -------------------------
# PASSWORD FUNCTIONS
# -------------------------

def hash_password(password, salt):

    # Convert password and salt to bytes.
    password_bytes = password.encode()
    salt_bytes = salt.encode()


    # Create a PBKDF2 password hash.
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password_bytes,
        salt_bytes,
        100000
    )


    # Return readable hexadecimal hash.
    return password_hash.hex()


def create_password_hash(password):

    # Generate a random salt.
    salt = os.urandom(16).hex()

    # Create hash using the salt.
    password_hash = hash_password(
        password,
        salt
    )

    return password_hash, salt


# -------------------------
# USER FUNCTIONS
# -------------------------

def add_user(username, email, password):

    # Create password hash and salt.
    password_hash, salt = create_password_hash(password)

    # Current time.
    created_at = datetime.now().isoformat()

    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    try:

        # Store the new user.
        cursor.execute(
            """
            INSERT INTO users
            (username, email, password_hash, salt, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                username,
                email,
                password_hash,
                salt,
                created_at
            )
        )

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        # Username or email already exists.
        return False

    finally:

        connection.close()


def get_user(username):

    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    # Find the user.
    cursor.execute(
        """
        SELECT
            id,
            username,
            email,
            password_hash,
            salt
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    connection.close()

    return user


def check_password(password, stored_hash, salt):

    # Hash the entered password using
    # the stored salt.
    new_hash = hash_password(
        password,
        salt
    )

    # Compare both hashes.
    return new_hash == stored_hash


# -------------------------
# DATABASE INITIALIZATION
# -------------------------

if __name__ == "__main__":

    create_database()

    print("CipherChat database ready.")