import sqlite3
import hashlib
import os
from datetime import datetime

import random
# Location of our SQLite database.
DATABASE = "database/cipherchat.db"


def create_database():

    # Connect to SQLite.
    connection = sqlite3.connect(DATABASE)

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


    connection.commit()

    connection.close()


# -------------------------
# PASSWORD FUNCTIONS
# -------------------------

def hash_password(password, salt):

    # Convert password and salt into bytes.
    password_bytes = password.encode()
    salt_bytes = salt.encode()


    # Create PBKDF2 password hash.
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password_bytes,
        salt_bytes,
        100000
    )


    # Convert hash to hexadecimal text.
    return password_hash.hex()


def create_password_hash(password):

    # Generate random salt.
    salt = os.urandom(16).hex()


    # Create password hash.
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

    # Get current time.
    created_at = datetime.now().isoformat()


    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    try:

        # Store user.
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

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Get user information.
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

    # Hash entered password using stored salt.
    new_hash = hash_password(
        password,
        salt
    )


    # Compare hashes.
    return new_hash == stored_hash


# -------------------------
# MESSAGE FUNCTIONS
# -------------------------

def get_user_id(username):

    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Find user ID from username.
    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE username = ?
        """,
        (username,)
    )


    result = cursor.fetchone()

    connection.close()


    # Return ID if user exists.
    if result is not None:
        return result[0]

    return None


def save_message(sender_username, receiver_username, message):

    # Find sender ID.
    sender_id = get_user_id(
        sender_username
    )


    # Find receiver ID if this is a private message.
    receiver_id = None

    if receiver_username is not None:

        receiver_id = get_user_id(
            receiver_username
        )


    # If sender doesn't exist, don't save.
    if sender_id is None:
        return


    # Current time.
    created_at = datetime.now().isoformat()


    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Store the message.
    #
    # room_id is NULL for now.
    # We'll use it when room chat is implemented.
    cursor.execute(
        """
        INSERT INTO messages
        (
            sender_id,
            receiver_id,
            room_id,
            message,
            created_at
        )
        VALUES (?, ?, NULL, ?, ?)
        """,
        (
            sender_id,
            receiver_id,
            message,
            created_at
        )
    )


    connection.commit()

    connection.close()


def get_messages(username):

    # Find the user's ID.
    user_id = get_user_id(username)


    if user_id is None:
        return []


    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Get recent messages involving this user.
    #
    # Broadcast:
    # receiver_id IS NULL
    #
    # Private:
    # sender_id = user
    # OR receiver_id = user
    cursor.execute(
        """
        SELECT
            sender_id,
            receiver_id,
            message
        FROM messages
        WHERE
            receiver_id IS NULL
            OR sender_id = ?
            OR receiver_id = ?
        ORDER BY id DESC
        LIMIT 10
        """,
        (
            user_id,
            user_id
        )
    )


    rows = cursor.fetchall()

    connection.close()


    # Convert IDs back into usernames.
    messages = []


    for sender_id, receiver_id, message in rows:

        # Get sender username.
        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute(
            "SELECT username FROM users WHERE id = ?",
            (sender_id,)
        )

        sender_result = cursor.fetchone()


        # Get receiver username.
        receiver_result = None

        if receiver_id is not None:

            cursor.execute(
                "SELECT username FROM users WHERE id = ?",
                (receiver_id,)
            )

            receiver_result = cursor.fetchone()


        connection.close()


        # Convert database IDs to usernames.
        sender = sender_result[0]

        receiver = None

        if receiver_result is not None:
            receiver = receiver_result[0]


        messages.append(
            (
                sender,
                receiver,
                message
            )
        )


    # We retrieved newest first.
    # Reverse so oldest appears first.
    messages.reverse()


    return messages

def create_room(username, room_name, room_type):

    # Find the owner's user ID.
    owner_id = get_user_id(username)

    # The owner must exist.
    if owner_id is None:
        return None


    # Generate a unique 6-digit room code.
    while True:

        room_code = str(
            random.randint(100000, 999999)
        )

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM rooms
            WHERE room_code = ?
            """,
            (room_code,)
        )

        existing_room = cursor.fetchone()

        connection.close()


        # Stop if the code is not already used.
        if existing_room is None:
            break


    # Get current time.
    created_at = datetime.now().isoformat()


    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Create the room.
    cursor.execute(
        """
        INSERT INTO rooms
        (
            room_code,
            room_name,
            owner_id,
            room_type,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            room_code,
            room_name,
            owner_id,
            room_type,
            created_at
        )
    )


    # Get the newly created room ID.
    room_id = cursor.lastrowid


    # Add the owner as the first room member.
    cursor.execute(
        """
        INSERT INTO room_members
        (
            room_id,
            user_id,
            role
        )
        VALUES (?, ?, ?)
        """,
        (
            room_id,
            owner_id,
            "owner"
        )
    )


    # Save changes.
    connection.commit()

    connection.close()


    # Return the room code.
    return room_code
def join_room(username, room_code):

    # Find the user's ID.
    user_id = get_user_id(username)

    # User must exist.
    if user_id is None:
        return False


    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Find the room.
    cursor.execute(
        """
        SELECT id
        FROM rooms
        WHERE room_code = ?
        """,
        (room_code,)
    )

    room = cursor.fetchone()


    # Room does not exist.
    if room is None:

        connection.close()

        return False


    room_id = room[0]


    # Check whether the user is already a member.
    cursor.execute(
        """
        SELECT user_id
        FROM room_members
        WHERE room_id = ?
        AND user_id = ?
        """,
        (
            room_id,
            user_id
        )
    )

    existing_member = cursor.fetchone()


    if existing_member is not None:

        connection.close()

        return False


    # Count current room members.
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM room_members
        WHERE room_id = ?
        """,
        (room_id,)
    )

    member_count = cursor.fetchone()[0]


    # Maximum room size is 10.
    if member_count >= 10:

        connection.close()

        return False


    # Add the user to the room.
    cursor.execute(
        """
        INSERT INTO room_members
        (
            room_id,
            user_id,
            role
        )
        VALUES (?, ?, ?)
        """,
        (
            room_id,
            user_id,
            "member"
        )
    )


    # Save the change.
    connection.commit()

    connection.close()


    return True
# -------------------------
# DATABASE INITIALIZATION
# -------------------------

if __name__ == "__main__":

    create_database()

    print("CipherChat database ready.")