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


# Store the sockets of all connected clients.
clients = []


def handle_client(client, address):

    # Each client has its own message buffer.
    buffer = ""

    print("Client connected:", address)

    # Keep communicating with this client.
    while True:

        try:
            # Receive data from this client.
            data = client.recv(1024)

            # If no data is received, the client closed the connection.
            if data == b"":
                print("Client disconnected:", address)
                break

            # Add the received data to this client's buffer.
            buffer = buffer + data.decode()

            # Check whether a complete message exists.
            while "\n" in buffer:

                # Get one complete message.
                # Keep the remaining data in the buffer.
                message, buffer = buffer.split("\n", 1)

                # Check if the client wants to leave.
                if message.lower() == "exit":
                    print("Client left:", address)
                    break

                # Display the message.
                print("Client", address, ":", message)

                # Add the sender's address to the message.
                broadcast_message = str(address) + ": " + message + "\n"

                # Send the message to every other connected client.
                for other_client in clients:

                    # Do not send the message back to the sender.
                    if other_client != client:

                        # Convert the message into bytes and send it.
                        other_client.send(broadcast_message.encode())

        except ConnectionResetError:

            # The client closed the connection unexpectedly.
            print("Client connection was reset:", address)
            break

    # Remove the client from the list.
    if client in clients:
        clients.remove(client)

    # Close this client's socket.
    client.close()


# Keep accepting new clients.
while True:

    # Wait for a new client.
    client, address = server.accept()

    # Add the new client to our list.
    clients.append(client)

    # Create a separate thread for this client.
    client_thread = threading.Thread(
        target=handle_client,
        args=(client, address)
    )

    # Start the client thread.
    client_thread.start()