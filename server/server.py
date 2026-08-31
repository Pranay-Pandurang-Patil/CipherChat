import socket
import threading
import sys
import os


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

SERVER_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

sys.path.append(PROJECT_ROOT)
sys.path.append(SERVER_FOLDER)


# =========================================================
# IMPORTS
# =========================================================

from auth import register_user, login_user

from database.database import (
    save_message,
    create_room,
    join_room,
    get_room,
    get_room_members,
    get_room_messages
)


# =========================================================
# SERVER SETTINGS
# =========================================================

HOST = "127.0.0.1"
PORT = 5000


# =========================================================
# INPUT LIMITS
# =========================================================

MAX_USERNAME_LENGTH = 20
MAX_EMAIL_LENGTH = 100
MAX_PASSWORD_LENGTH = 100
MAX_ROOM_NAME_LENGTH = 50
MAX_MESSAGE_LENGTH = 500
MAX_ROOM_CODE_LENGTH = 6


# =========================================================
# CREATE SERVER SOCKET
# =========================================================

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)


# Allow quick server restart.
server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)


# Bind server.
server.bind(
    (HOST, PORT)
)


# Start listening.
server.listen()


print("CipherChat server started.")
print("Waiting for clients...")


# =========================================================
# CONNECTED CLIENTS
# =========================================================

# socket -> username
clients = {}


# socket -> room_code
client_rooms = {}


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def receive_text(client):

    # Receive data from client.
    data = client.recv(1024)


    # Client closed connection.
    if data == b"":

        return None


    # Decode safely.
    return data.decode(
        "utf-8",
        errors="replace"
    ).strip()


def send_message(client, message):

    # Add newline delimiter.
    message = message + "\n"


    # Encode using UTF-8.
    data = message.encode(
        "utf-8"
    )


    # Send message.
    client.send(data)


def valid_length(value, maximum):

    # Check maximum length.
    return len(value) <= maximum


# =========================================================
# CLIENT HANDLER
# =========================================================

def handle_client(client, address):

    # Buffer for incoming chat messages.
    buffer = ""

    # Username before authentication.
    username = ""

    # Current room.
    room_code = None


    print(
        "Client connected:",
        address
    )


    try:

        # =================================================
        # AUTHENTICATION
        # =================================================

        send_message(
            client,
            "REGISTER or LOGIN?"
        )


        option = receive_text(
            client
        )


        if option is None:

            return


        option = option.upper()


        # Validate option.
        if option not in [
            "REGISTER",
            "LOGIN"
        ]:

            send_message(
                client,
                "Invalid option."
            )

            return


        # =================================================
        # USERNAME
        # =================================================

        send_message(
            client,
            "USERNAME?"
        )


        username = receive_text(
            client
        )


        if username is None:

            return


        # Validate username length.
        if not valid_length(
            username,
            MAX_USERNAME_LENGTH
        ):

            send_message(
                client,
                "Username is too long."
            )

            return


        # =================================================
        # EMAIL
        # =================================================

        if option == "REGISTER":

            send_message(
                client,
                "EMAIL?"
            )


            email = receive_text(
                client
            )


            if email is None:

                return


            # Validate email length.
            if not valid_length(
                email,
                MAX_EMAIL_LENGTH
            ):

                send_message(
                    client,
                    "Email is too long."
                )

                return


        # =================================================
        # PASSWORD
        # =================================================

        send_message(
            client,
            "PASSWORD?"
        )


        password = receive_text(
            client
        )


        if password is None:

            return


        # Validate password length.
        if not valid_length(
            password,
            MAX_PASSWORD_LENGTH
        ):

            send_message(
                client,
                "Password is too long."
            )

            return


        # =================================================
        # REGISTER
        # =================================================

        if option == "REGISTER":

            success = register_user(
                username,
                email,
                password
            )


            if not success:

                send_message(
                    client,
                    "Registration failed."
                )

                return


            print(
                username,
                "registered successfully."
            )


        # =================================================
        # LOGIN
        # =================================================

        else:

            success = login_user(
                username,
                password
            )


            if not success:

                send_message(
                    client,
                    "Login failed."
                )

                return


            print(
                username,
                "logged in successfully."
            )


        # =================================================
        # DUPLICATE ONLINE USER
        # =================================================

        if username in clients.values():

            send_message(
                client,
                "User is already online."
            )

            return


        # Store authenticated client.
        clients[client] = username


        # Authentication successful.
        send_message(
            client,
            "AUTHENTICATION SUCCESS"
        )


        # =================================================
        # ROOM MENU
        # =================================================

        send_message(
            client,
            "ROOM MENU: CREATE or JOIN"
        )


        room_option = receive_text(
            client
        )


        if room_option is None:

            return


        room_option = room_option.upper()


        # =================================================
        # CREATE ROOM
        # =================================================

        if room_option == "CREATE":

            send_message(
                client,
                "ROOM NAME?"
            )


            room_name = receive_text(
                client
            )


            if room_name is None:

                return


            # Validate room name.
            if not valid_length(
                room_name,
                MAX_ROOM_NAME_LENGTH
            ):

                send_message(
                    client,
                    "Room name is too long."
                )

                return


            # Current project uses permanent rooms.
            room_type = "permanent"


            # Create room.
            room_code = create_room(
                username,
                room_name,
                room_type
            )


            if room_code is None:

                send_message(
                    client,
                    "Room creation failed."
                )

                return


            # Store user's current room.
            client_rooms[client] = room_code


            print(
                username,
                "created room",
                room_code
            )


            send_message(
                client,
                "ROOM CREATED: "
                + room_code
            )


        # =================================================
        # JOIN ROOM
        # =================================================

        elif room_option == "JOIN":

            send_message(
                client,
                "ROOM CODE?"
            )


            room_code = receive_text(
                client
            )


            if room_code is None:

                return


            # Validate room code.
            if (
                len(room_code) != MAX_ROOM_CODE_LENGTH
                or not room_code.isdigit()
            ):

                send_message(
                    client,
                    "Invalid room code."
                )

                return


            # Join room.
            success = join_room(
                username,
                room_code
            )


            if not success:

                send_message(
                    client,
                    "Unable to join room."
                )

                return


            # Store user's current room.
            client_rooms[client] = room_code


            print(
                username,
                "joined room",
                room_code
            )


            send_message(
                client,
                "ROOM JOINED: "
                + room_code
            )


        # =================================================
        # INVALID ROOM OPTION
        # =================================================

        else:

            send_message(
                client,
                "Invalid room option."
            )

            return


        # =================================================
        # ROOM INFORMATION
        # =================================================

        room = get_room(
            room_code
        )


        if room is not None:

            room_name = room[2]


            send_message(
                client,
                "ROOM: "
                + room_name
            )


        # Get room members.
        members = get_room_members(
            room_code
        )


        send_message(
            client,
            "--- Room Members ---"
        )


        for member_username, role in members:

            send_message(
                client,
                member_username
                + " ["
                + role
                + "]"
            )


        send_message(
            client,
            "--- End Members ---"
        )


        # =================================================
        # ROOM MESSAGE HISTORY
        # =================================================

        history = get_room_messages(
            room_code
        )


        send_message(
            client,
            "--- Recent Messages ---"
        )


        for sender, message in history:

            send_message(
                client,
                sender
                + ": "
                + message
            )


        send_message(
            client,
            "--- End of History ---"
        )


        # =================================================
        # CHAT LOOP
        # =================================================

        while True:

            data = client.recv(
                1024
            )


            # Client disconnected.
            if data == b"":

                print(
                    username,
                    "disconnected."
                )

                break


            # Decode safely.
            buffer = (
                buffer
                + data.decode(
                    "utf-8",
                    errors="replace"
                )
            )


            # =================================================
            # MESSAGE FRAMING
            # =================================================

            while "\n" in buffer:

                message, buffer = (
                    buffer.split(
                        "\n",
                        1
                    )
                )


                # =================================================
                # MESSAGE LENGTH LIMIT
                # =================================================

                if not valid_length(
                    message,
                    MAX_MESSAGE_LENGTH
                ):

                    send_message(
                        client,
                        "Message is too long. Maximum 500 characters."
                    )

                    continue


                # =================================================
                # EXIT
                # =================================================

                if message.lower() == "exit":

                    print(
                        username,
                        "left the chat."
                    )

                    return


                # =================================================
                # PRIVATE MESSAGE
                # =================================================

                if message.startswith("@"):

                    parts = message.split(
                        " ",
                        1
                    )


                    # Validate private message format.
                    if len(parts) < 2:

                        send_message(
                            client,
                            "Usage: @username message"
                        )

                        continue


                    target_username = (
                        parts[0][1:]
                    )


                    private_text = parts[1]


                    # Find target client.
                    target_client = None


                    for other_client in clients:

                        if (
                            clients[other_client]
                            == target_username
                        ):

                            target_client = (
                                other_client
                            )

                            break


                    # Target is not online.
                    if target_client is None:

                        send_message(
                            client,
                            "User not found."
                        )

                        continue


                    # Save private message.
                    save_message(
                        username,
                        target_username,
                        private_text
                    )


                    # Create private message.
                    private_message = (
                        "[Private] "
                        + username
                        + ": "
                        + private_text
                    )


                    # Send only to target.
                    send_message(
                        target_client,
                        private_message
                    )


                # =================================================
                # ROOM MESSAGE
                # =================================================

                else:

                    print(
                        username
                        + " ["
                        + room_code
                        + "]: "
                        + message
                    )


                    # Save message with room code.
                    save_message(
                        username,
                        None,
                        message,
                        room_code
                    )


                    # Create room message.
                    room_message = (
                        username
                        + ": "
                        + message
                    )


                    # Send only to same room.
                    for other_client in clients:

                        other_room = (
                            client_rooms.get(
                                other_client
                            )
                        )


                        if (
                            other_client != client
                            and other_room == room_code
                        ):

                            send_message(
                                other_client,
                                room_message
                            )


    except ConnectionResetError:

        print(
            username,
            "connection was reset."
        )


    except UnicodeError:

        print(
            username,
            "sent invalid text data."
        )


    finally:

        # Remove authenticated client.
        if client in clients:

            del clients[client]


        # Remove room information.
        if client in client_rooms:

            del client_rooms[client]


        # Close socket.
        client.close()


# =========================================================
# MAIN SERVER LOOP
# =========================================================

while True:

    try:

        # Wait for a new client.
        client, address = server.accept()


        # Create client thread.
        client_thread = threading.Thread(
            target=handle_client,
            args=(client, address)
        )


        # Start thread.
        client_thread.start()


    except KeyboardInterrupt:

        print(
            "\nCipherChat server shutting down."
        )

        break


# Close server socket.
server.close()