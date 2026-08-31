import sqlite3
import hashlib
import os
import random
from datetime import datetime


# Location of our SQLite database.
DATABASE = "database/cipherchat.db"


# =========================================================
# DATABASE SETUP
# =========================================================

def create_database():

    # Connect to SQLite.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # -------------------------
    # USERS TABLE
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
    # ROOMS TABLE
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
    # ROOM MEMBERS TABLE
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
    # MESSAGES TABLE
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


    # Save database changes.
    connection.commit()

    # Close database connection.
    connection.close()


# =========================================================
# PASSWORD FUNCTIONS
# =========================================================

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


    # Convert hash into hexadecimal text.
    return password_hash.hex()


def create_password_hash(password):

    # Generate a random salt.
    salt = os.urandom(16).hex()


    # Create password hash.
    password_hash = hash_password(
        password,
        salt
    )


    return password_hash, salt


# =========================================================
# USER FUNCTIONS
# =========================================================

def add_user(username, email, password):

    # Create password hash and salt.
    password_hash, salt = create_password_hash(
        password
    )


    # Get current time.
    created_at = datetime.now().isoformat()


    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    try:

        # Insert new user.
        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                email,
                password_hash,
                salt,
                created_at
            )
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


        # Save changes.
        connection.commit()

        return True


    except sqlite3.IntegrityError:

        # Username or email already exists.
        return False


    finally:

        # Close database connection.
        connection.close()


def get_user(username):

    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Find user by username.
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


    # Get user.
    user = cursor.fetchone()


    # Close database.
    connection.close()


    return user


def get_user_id(username):

    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Find user's ID.
    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE username = ?
        """,
        (username,)
    )


    result = cursor.fetchone()


    # Close database.
    connection.close()


    # Return ID if user exists.
    if result is not None:
        return result[0]


    return None


def check_password(password, stored_hash, salt):

    # Hash the entered password using
    # the stored salt.
    new_hash = hash_password(
        password,
        salt
    )


    # Compare hashes.
    return new_hash == stored_hash


# =========================================================
# MESSAGE FUNCTIONS
# =========================================================

def save_message(
    sender_username,
    receiver_username,
    message,
    room_code=None
):

    # Find sender ID.
    sender_id = get_user_id(
        sender_username
    )


    # Sender must exist.
    if sender_id is None:
        return False


    # Receiver ID is only needed
    # for 1-to-1 messages.
    receiver_id = None


    if receiver_username is not None:

        receiver_id = get_user_id(
            receiver_username
        )


        # Receiver must exist.
        if receiver_id is None:
            return False


    # Room ID is only needed
    # for room messages.
    room_id = None


    if room_code is not None:

        # Find room.
        room = get_room(
            room_code
        )


        # Room must exist.
        if room is None:
            return False


        room_id = room[0]


    # Get current time.
    created_at = datetime.now().isoformat()


    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Store message.
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
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            sender_id,
            receiver_id,
            room_id,
            message,
            created_at
        )
    )


    # Save changes.
    connection.commit()

    # Close database.
    connection.close()


    return True


def get_messages(username):

    # Find user's ID.
    user_id = get_user_id(
        username
    )


    if user_id is None:
        return []


    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Get recent messages involving the user.
    #
    # This currently handles:
    #
    # 1. Broadcast messages
    # 2. Private messages
    #
    # Room-specific history will be handled
    # separately when the room chat is finalized.
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


    # Close database connection.
    connection.close()


    messages = []


    # Convert IDs back to usernames.
    for sender_id, receiver_id, message in rows:

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()


        # Find sender username.
        cursor.execute(
            """
            SELECT username
            FROM users
            WHERE id = ?
            """,
            (sender_id,)
        )


        sender_result = cursor.fetchone()


        # Find receiver username if required.
        receiver_result = None


        if receiver_id is not None:

            cursor.execute(
                """
                SELECT username
                FROM users
                WHERE id = ?
                """,
                (receiver_id,)
            )


            receiver_result = cursor.fetchone()


        connection.close()


        # Convert sender ID to username.
        sender = sender_result[0]


        # Convert receiver ID to username.
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


    # Newest messages were retrieved first.
    # Reverse them for normal chronological order.
    messages.reverse()


    return messages


# =========================================================
# ROOM FUNCTIONS
# =========================================================

def create_room(username, room_name, room_type):

    # Find owner's ID.
    owner_id = get_user_id(
        username
    )


    # Owner must exist.
    if owner_id is None:
        return None


    # Generate a unique six-digit room code.
    while True:

        room_code = str(
            random.randint(
                100000,
                999999
            )
        )


        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()


        # Check whether code already exists.
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


        # Use the code if it is unique.
        if existing_room is None:
            break


    # Get current time.
    created_at = datetime.now().isoformat()


    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Create room.
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


    # Get newly created room ID.
    room_id = cursor.lastrowid


    # Automatically add owner as first member.
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


    # Return room code.
    return room_code


def join_room(username, room_code):

    # Find user's ID.
    user_id = get_user_id(
        username
    )


    # User must exist.
    if user_id is None:
        return False


    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Find room.
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


    # Check whether user is already a member.
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


    # Count current members.
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


    # Add user as member.
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


    # Save changes.
    connection.commit()

    connection.close()


    return True


def get_room(room_code):

    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Find room.
    cursor.execute(
        """
        SELECT
            id,
            room_code,
            room_name,
            owner_id,
            room_type,
            created_at
        FROM rooms
        WHERE room_code = ?
        """,
        (room_code,)
    )


    room = cursor.fetchone()


    connection.close()


    return room


def get_room_members(room_code):

    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Get room members and their roles.
    cursor.execute(
        """
        SELECT
            users.username,
            room_members.role
        FROM room_members
        JOIN rooms
            ON room_members.room_id = rooms.id
        JOIN users
            ON room_members.user_id = users.id
        WHERE rooms.room_code = ?
        ORDER BY users.username
        """,
        (room_code,)
    )


    members = cursor.fetchall()


    connection.close()


    return members

def get_room_messages(room_code):

    # Find the room.
    room = get_room(room_code)

    # Room does not exist.
    if room is None:
        return []


    # Get room ID.
    room_id = room[0]


    # Connect to database.
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # Get the latest 20 messages from this room.
    cursor.execute(
        """
        SELECT
            users.username,
            messages.message
        FROM messages
        JOIN users
            ON messages.sender_id = users.id
        WHERE messages.room_id = ?
        ORDER BY messages.id DESC
        LIMIT 20
        """,
        (room_id,)
    )


    rows = cursor.fetchall()


    connection.close()


    # Convert newest-first results into
    # chronological order.
    rows.reverse()


    return rows

# =========================================================
# DATABASE INITIALIZATION
# =========================================================

if __name__ == "__main__":

    create_database()

    print(
        "CipherChat database ready."
    )