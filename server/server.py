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


def handle_client(client, address):

    # Each client has its own message buffer.
    buffer = ""

    print("Client connected:", address)

    try:

        # Ask the client for a username.
        client.send("USERNAME?\n".encode())

        # Receive the username.
        data = client.recv(1024)

        # Convert bytes into text.
        username = data.decode().strip()

        # Store the client and username.
        clients[client] = username

        print(username, "joined the chat.")

        # Send a welcome message.
        client.send("Welcome to CipherChat!\n".encode())


        # Keep communicating with this client.
        while True:

            # Receive data from this client.
            data = client.recv(1024)

            # Check if the client closed the connection.
            if data == b"":
                print(username, "disconnected.")
                break

            # Add received data to the client's buffer.
            buffer = buffer + data.decode()

            # Process complete messages.
            while "\n" in buffer:

                # Separate one complete message.
                message, buffer = buffer.split("\n", 1)

                # Check if the client wants to leave.
                if message.lower() == "exit":
                    print(username, "left the chat.")
                    return

                # Display the message on the server.
                print(username + ":", message)

                # Create the message that other clients will receive.
                broadcast_message = username + ": " + message + "\n"

                # Send the message to every other client.
                for other_client in clients:

                    # Don't send the message back to the sender.
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