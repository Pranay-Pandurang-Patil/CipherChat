import sqlite3


# Location of our SQLite database file.
DATABASE = "database/cipherchat.db"


def create_database():

    # Connect to the SQLite database.
    # If the file does not exist, SQLite creates it.
    connection = sqlite3.connect(DATABASE)

    # Create a cursor to execute SQL commands.
    cursor = connection.cursor()

    # Create the users table.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
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


def add_user(username):

    # Connect to the database.
    connection = sqlite3.connect(DATABASE)

    # Create a cursor.
    cursor = connection.cursor()

    try:

        # Add the username to the users table.
        cursor.execute(
            "INSERT INTO users (username) VALUES (?)",
            (username,)
        )

        # Save the change.
        connection.commit()

        # Username was successfully added.
        return True

    except sqlite3.IntegrityError:

        # This happens if the username already exists.
        return False

    finally:

        # Close the database connection.
        connection.close()


# Create the database and tables.
create_database()

print("CipherChat database ready.")