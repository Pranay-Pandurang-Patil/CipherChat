import socket
import threading


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


def send_private_message(sender, target_username, message):

    # Search through all connected clients.
    for client_socket in clients:

        # Get the username belonging to this socket.
        username = clients[client_socket]

        # Check if this is the requested recipient.
        if username == target_username:

            # Create the private message.
            private_message = "[Private] " + sender + ": " + message + "\n"

            # Send the message only to this client.
            client_socket.send(private_message.encode())

            # Tell the caller that the message was sent.
            return True

    # Target username was not found.
    return False


def handle_client(client, address):

    # Each client has its own message buffer.
    buffer = ""

    # Keep the username empty until validation is completed.
    username = ""

    print("Client connected:", address)

    try:

        # Ask the client for a username.
        client.send("USERNAME?\n".encode())

        # Receive the username.
        data = client.recv(1024)

        # Convert bytes into text.
        username = data.decode().strip()

        # Check if the username is valid.
        if not valid_username(username):

            client.send(
                "Invalid username. Use letters, numbers and underscore only.\n".encode()
            )

            client.close()
            return

        # Check if the username is already being used.
        if username in clients.values():

            client.send(
                "Username already taken.\n".encode()
            )

            client.close()
            return

        # Store the client and username.
        clients[client] = username

        print(username, "joined the chat.")

        # Send a welcome message.
        client.send(
            "Welcome to CipherChat!\n".encode()
        )

        # Keep communicating with this client.
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

                # Check if this is a private message.
                if message.startswith("@"):

                    # Split the target username and message.
                    parts = message.split(" ", 1)

                    # Make sure a message was provided.
                    if len(parts) < 2:
                        client.send(
                            "Usage: @username message\n".encode()
                        )
                        continue

                    # Remove @ from the username.
                    target_username = parts[0][1:]

                    # Get the actual message.
                    private_text = parts[1]

                    # Send the private message.
                    sent = send_private_message(
                        username,
                        target_username,
                        private_text
                    )

                    # Tell the sender if the username was not found.
                    if not sent:
                        client.send(
                            "User not found.\n".encode()
                        )

                else:

                    # Display normal messages on the server.
                    print(username + ":", message)

                    # Create the broadcast message.
                    broadcast_message = username + ": " + message + "\n"

                    # Send the message to every other client.
                    for other_client in clients:

                        # Do not send the message back to the sender.
                        if other_client != client:

                            other_client.send(
                                broadcast_message.encode()
                            )

    except ConnectionResetError:

        # Handle an unexpected connection close.
        print(username, "connection was reset.")

    finally:

        # Remove the client from the dictionary.
        if client in clients:
            del clients[client]

        # Close the client's socket.
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