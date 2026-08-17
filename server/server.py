import socket
import threading
import sys
import os


# Add the CipherChat project folder to Python's module search path.
# This allows server.py to access the database folder.
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(PROJECT_ROOT)


# Import our database functions.
from database.database import add_user, get_user, check_password


# IP address where our server will listen.
# 127.0.0.1 means this computer.
HOST = "127.0.0.1"

# Port used for communication.
PORT = 5000


# Create a TCP socket.
# AF_INET = IPv4
# SOCK_STREAM = TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Attach the socket to our IP address and port.
server.bind((HOST, PORT))


# Start listening for incoming clients.
server.listen()

print("CipherChat server started.")
print("Waiting for clients...")


# Store connected clients and their usernames.
# Format:
# socket -> username
clients = {}


def valid_username(username):

    # Username cannot be empty.
    if username == "":
        return False

    # Username cannot be longer than 20 characters.
    if len(username) > 20:
        return False

    # Check every character.
    for character in username:

        # Allow letters, numbers and underscore.
        if not (character.isalnum() or character == "_"):
            return False

    return True


def handle_client(client, address):

    # Each client has its own message buffer.
    buffer = ""

    # Username remains empty until login/register succeeds.
    username = ""

    print("Client connected:", address)

    try:

        # Ask the client whether they want to register or login.
        client.send(
            "REGISTER or LOGIN?\n".encode()
        )

        # Receive the selected option.
        data = client.recv(1024)

        option = data.decode().strip().upper()


        # Only REGISTER and LOGIN are accepted.
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


        # Validate username.
        if not valid_username(username):

            client.send(
                "Invalid username.\n".encode()
            )

            client.close()
            return


        # Ask for password.
        client.send(
            "PASSWORD?\n".encode()
        )

        data = client.recv(1024)

        password = data.decode().strip()


        # -------------------------
        # REGISTER
        # -------------------------

        if option == "REGISTER":

            # Add the new user to SQLite.
            success = add_user(username, password)

            # Check whether registration succeeded.
            if not success:

                client.send(
                    "Username already registered.\n".encode()
                )

                client.close()
                return

            print(username, "registered successfully.")


        # -------------------------
        # LOGIN
        # -------------------------

        else:

            # Get the user's stored information.
            user = get_user(username)

            # Check if the account exists.
            if user is None:

                client.send(
                    "User does not exist.\n".encode()
                )

                client.close()
                return


            # Get stored password information.
            stored_username = user[0]
            stored_hash = user[1]
            salt = user[2]


            # Check the password.
            if not check_password(
                password,
                stored_hash,
                salt
            ):

                client.send(
                    "Incorrect password.\n".encode()
                )

                client.close()
                return


            print(stored_username, "logged in successfully.")


        # Check whether this user is already online.
        if username in clients.values():

            client.send(
                "User is already online.\n".encode()
            )

            client.close()
            return


        # Store the authenticated client.
        clients[client] = username


        # Tell the client authentication succeeded.
        client.send(
            "AUTHENTICATION SUCCESS\n".encode()
        )


        # -------------------------
        # CHAT
        # -------------------------

        while True:

            # Receive data from the client.
            data = client.recv(1024)


            # Check if the client closed the connection.
            if data == b"":

                print(username, "disconnected.")
                break


            # Add received data to the buffer.
            buffer = buffer + data.decode()


            # Process complete messages.
            while "\n" in buffer:

                # Separate one complete message.
                message, buffer = buffer.split("\n", 1)


                # Check if the client wants to leave.
                if message.lower() == "exit":

                    print(username, "left the chat.")
                    return


                # Check for private messaging.
                if message.startswith("@"):

                    parts = message.split(" ", 1)


                    # Make sure a message was provided.
                    if len(parts) < 2:

                        client.send(
                            "Usage: @username message\n".encode()
                        )

                        continue


                    # Get target username.
                    target_username = parts[0][1:]


                    # Get private message.
                    private_text = parts[1]


                    # Search for the target client.
                    target_client = None

                    for other_client in clients:

                        if clients[other_client] == target_username:

                            target_client = other_client
                            break


                    # Check if target exists.
                    if target_client is None:

                        client.send(
                            "User not found.\n".encode()
                        )

                        continue


                    # Create private message.
                    private_message = (
                        "[Private] "
                        + username
                        + ": "
                        + private_text
                        + "\n"
                    )


                    # Send only to the target.
                    target_client.send(
                        private_message.encode()
                    )


                else:

                    # Display normal message.
                    print(username + ":", message)


                    # Create broadcast message.
                    broadcast_message = (
                        username
                        + ": "
                        + message
                        + "\n"
                    )


                    # Send to every other client.
                    for other_client in clients:

                        if other_client != client:

                            other_client.send(
                                broadcast_message.encode()
                            )


    except ConnectionResetError:

        # Handle unexpected connection close.
        print(username, "connection was reset.")


    finally:

        # Remove the client from the online client list.
        if client in clients:

            del clients[client]


        # Close the socket.
        client.close()


# Keep accepting new clients.
while True:

    # Wait for a new client.
    client, address = server.accept()


    # Create a thread for this client.
    client_thread = threading.Thread(
        target=handle_client,
        args=(client, address)
    )


    # Start the client thread.
    client_thread.start()