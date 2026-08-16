import sqlite3
import hashlib
import os


# Location of our SQLite database file.
DATABASE = "database/cipherchat.db"


def create_database():

    # Connect to the SQLite database.
    connection = sqlite3.connect(DATABASE)

    # Create a cursor to execute SQL commands.
    cursor = connection.cursor()

    # Create the users table.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)

    # Create the messages table.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT,
            message TEXT NOT NULL
        )
    """)

    # Save the changes.
    connection.commit()

    # Close the database connection.
    connection.close()


def hash_password(password, salt):

    # Convert the password and salt into bytes.
    password_bytes = password.encode()
    salt_bytes = salt.encode()

    # Create a password hash using PBKDF2.
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password_bytes,
        salt_bytes,
        100000
    )

    # Convert the hash into readable hexadecimal text.
    return password_hash.hex()


def create_password_hash(password):

    # Generate a random salt.
    salt = os.urandom(16).hex()

    # Create the password hash using the salt.
    password_hash = hash_password(password, salt)

    # Return both values.
    return password_hash, salt


def add_user(username, password):

    # Create a password hash and salt.
    password_hash, salt = create_password_hash(password)

    # Connect to the database.
    connection = sqlite3.connect(DATABASE)

    # Create a cursor.
    cursor = connection.cursor()

    try:

        # Store the username, hash and salt.
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, salt)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, salt)
        )

        # Save the new user.
        connection.commit()

        # User was successfully created.
        return True

    except sqlite3.IntegrityError:

        # Username already exists.
        return False

    finally:

        # Close the database connection.
        connection.close()


def get_user(username):

    # Connect to the database.
    connection = sqlite3.connect(DATABASE)

    # Create a cursor.
    cursor = connection.cursor()

    # Search for the username.
    cursor.execute(
        """
        SELECT username, password_hash, salt
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    # Get the user information.
    user = cursor.fetchone()

    # Close the database connection.
    connection.close()

    # Return the user information.
    return user


def check_password(password, stored_hash, salt):

    # Create a hash from the password entered by the user.
    new_hash = hash_password(password, salt)

    # Compare the new hash with the stored hash.
    return new_hash == stored_hash


# Create the database and tables.
create_database()

print("CipherChat database ready.")