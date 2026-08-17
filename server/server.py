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


# Add both folders to Python's module search path.
sys.path.append(PROJECT_ROOT)
sys.path.append(SERVER_FOLDER)


# Import authentication functions.
from auth import register_user, login_user

# Import the database function for saving messages.
from database.database import save_message, get_messages


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

            # Use the authentication module.
            success = register_user(
                username,
                password
            )

            # Check registration result.
            if not success:

                client.send(
                    "Registration failed.\n".encode()
                )

                client.close()
                return

            print(username, "registered successfully.")


        # -------------------------
        # LOGIN
        # -------------------------

        else:

            # Use the authentication module.
            success = login_user(
                username,
                password
            )

            # Check login result.
            if not success:

                client.send(
                    "Login failed.\n".encode()
                )

                client.close()
                return

            print(username, "logged in successfully.")


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

        # Get the user's recent message history.
        history = get_messages(username)


# Send a history header.
        client.send(
    "--- Recent Messages ---\n".encode()
)


# Send each previous message to the client.
        for sender, receiver, message in history:

    # Private message.
          if receiver is not None:

            history_message = (
            "[Private] "
            + sender
            + ": "
            + message
            + "\n"
        )

    # Broadcast message.
          else:

            history_message = (
             sender
            + ": "
            + message
            + "\n"
        )


    # Send the history message.
          client.send(history_message.encode())


# Mark the end of the history.
        client.send(
    "--- End of History ---\n".encode()
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


                # -------------------------
                # PRIVATE MESSAGE
                # -------------------------

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


                    # Save the private message to SQLite.
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


                    # Send only to the target.
                    target_client.send(
                        private_message.encode()
                    )


                # -------------------------
                # BROADCAST MESSAGE
                # -------------------------

                else:

                    # Display normal message.
                    print(username + ":", message)


                    # Save the broadcast message to SQLite.
                    save_message(
                        username,
                        None,
                        message
                    )


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