import socket
import threading
import sys
import os


# Get the CipherChat project folder.
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Get the server folder.
SERVER_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)


# Add project folders to Python's module search path.
sys.path.append(PROJECT_ROOT)
sys.path.append(SERVER_FOLDER)


# Import authentication functions.
from auth import register_user, login_user

# Import database functions.
from database.database import save_message, get_messages


# IP address where our server will listen.
HOST = "127.0.0.1"

# Port used for communication.
PORT = 5000


# Create TCP socket.
server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)


# Attach socket to IP and port.
server.bind((HOST, PORT))


# Start listening.
server.listen()

print("CipherChat server started.")
print("Waiting for clients...")


# Store connected clients.
# Format:
# socket -> username
clients = {}


def handle_client(client, address):

    # Buffer for incoming messages.
    buffer = ""

    # Username is empty until authentication succeeds.
    username = ""

    print("Client connected:", address)

    try:

        # Ask whether the user wants to register or login.
        client.send(
            "REGISTER or LOGIN?\n".encode()
        )

        # Receive option.
        data = client.recv(1024)

        option = data.decode().strip().upper()


        # Validate option.
        if option not in ["REGISTER", "LOGIN"]:

            client.send(
                "Invalid option.\n".encode()
            )

            client.close()
            return


        # Ask for username.
        client.send(
            "USERNAME?\n".encode()
        )

        data = client.recv(1024)

        username = data.decode().strip()


        # -------------------------
        # REGISTER
        # -------------------------

        if option == "REGISTER":

            # Ask for email only during registration.
            client.send(
                "EMAIL?\n".encode()
            )

            data = client.recv(1024)

            email = data.decode().strip()


        # -------------------------
        # PASSWORD
        # -------------------------

        client.send(
            "PASSWORD?\n".encode()
        )

        data = client.recv(1024)

        password = data.decode().strip()


        # -------------------------
        # REGISTER
        # -------------------------

        if option == "REGISTER":

            # Register username + email + password.
            success = register_user(
                username,
                email,
                password
            )

            if not success:

                client.send(
                    "Registration failed.\n".encode()
                )

                client.close()
                return

            print(
                username,
                "registered successfully."
            )


        # -------------------------
        # LOGIN
        # -------------------------

        else:

            # Authenticate existing user.
            success = login_user(
                username,
                password
            )

            if not success:

                client.send(
                    "Login failed.\n".encode()
                )

                client.close()
                return

            print(
                username,
                "logged in successfully."
            )


        # Check if this user is already online.
        if username in clients.values():

            client.send(
                "User is already online.\n".encode()
            )

            client.close()
            return


        # Store authenticated client.
        clients[client] = username


        # Authentication succeeded.
        client.send(
            "AUTHENTICATION SUCCESS\n".encode()
        )


        # -------------------------
        # MESSAGE HISTORY
        # -------------------------

        history = get_messages(username)


        client.send(
            "--- Recent Messages ---\n".encode()
        )


        # Send previous messages.
        for sender, receiver, message in history:

            if receiver is not None:

                history_message = (
                    "[Private] "
                    + sender
                    + ": "
                    + message
                    + "\n"
                )

            else:

                history_message = (
                    sender
                    + ": "
                    + message
                    + "\n"
                )


            client.send(
                history_message.encode()
            )


        client.send(
            "--- End of History ---\n".encode()
        )


        # -------------------------
        # CHAT
        # -------------------------

        while True:

            # Receive data.
            data = client.recv(1024)


            # Client disconnected.
            if data == b"":

                print(
                    username,
                    "disconnected."
                )

                break


            # Add data to buffer.
            buffer = buffer + data.decode()


            # Process complete messages.
            while "\n" in buffer:

                message, buffer = buffer.split(
                    "\n",
                    1
                )


                # Exit command.
                if message.lower() == "exit":

                    print(
                        username,
                        "left the chat."
                    )

                    return


                # -------------------------
                # PRIVATE MESSAGE
                # -------------------------

                if message.startswith("@"):

                    parts = message.split(
                        " ",
                        1
                    )


                    if len(parts) < 2:

                        client.send(
                            "Usage: @username message\n".encode()
                        )

                        continue


                    target_username = parts[0][1:]

                    private_text = parts[1]


                    # Find target client.
                    target_client = None

                    for other_client in clients:

                        if clients[other_client] == target_username:

                            target_client = other_client

                            break


                    # Target not online.
                    if target_client is None:

                        client.send(
                            "User not found.\n".encode()
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
                        + "\n"
                    )


                    # Send only to target.
                    target_client.send(
                        private_message.encode()
                    )


                # -------------------------
                # BROADCAST
                # -------------------------

                else:

                    print(
                        username
                        + ": "
                        + message
                    )


                    # Save broadcast message.
                    save_message(
                        username,
                        None,
                        message
                    )


                    broadcast_message = (
                        username
                        + ": "
                        + message
                        + "\n"
                    )


                    # Send to other connected users.
                    for other_client in clients:

                        if other_client != client:

                            other_client.send(
                                broadcast_message.encode()
                            )


    except ConnectionResetError:

        print(
            username,
            "connection was reset."
        )


    finally:

        # Remove disconnected client.
        if client in clients:

            del clients[client]


        # Close socket.
        client.close()


# Keep accepting clients.
while True:

    client, address = server.accept()


    # Give each client its own thread.
    client_thread = threading.Thread(
        target=handle_client,
        args=(client, address)
    )


    client_thread.start()