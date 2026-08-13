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


# Start waiting for incoming connections.
server.listen()

print("CipherChat server started.")
print("Waiting for a client...")


# accept() pauses the program until a client connects.
# It returns:
# 1. A new socket for communicating with the client.
# 2. The client's IP address and port.
client, address = server.accept()

print("Client connected:", address)

def receive_messages():

    # Store data that has not formed a complete message yet.
    buffer = ""

    # Keep waiting for messages from the client.
    while True:

        try:
            # Receive data from the client.
            data = client.recv(1024)

            # Check if the client closed the connection.
            if data == b"":
                print("Client disconnected.")
                break

            # Convert bytes into text.
            buffer = buffer + data.decode()

            # Process every complete message in the buffer.
            while "\n" in buffer:

                # Split the first complete message from the remaining data.
                message, buffer = buffer.split("\n", 1)

                # Check if the client wants to leave.
                if message.lower() == "exit":
                    print("Client left the chat.")
                    return

                # Display the client's message.
                print("Client:", message)

        except ConnectionResetError:
            # The client closed the connection unexpectedly.
            print("Client connection was reset.")
            break

# Create a thread for receiving client messages.
receive_thread = threading.Thread(target=receive_messages)

# Start the receiving thread.
receive_thread.start()


# Main program is now used for sending messages.
while True:

    # Ask the server user for a reply.
    reply = input("Server: ")

    # Convert the reply into bytes.
    reply = input("Server: ")

# Add a newline to mark the end of our message.
    reply = reply + "\n"

# Convert the reply into bytes.
    data = reply.encode()

# Send the reply to the client.
    client.send(data)

    # Stop if the server user wants to exit.
    if reply.lower() == "exit":
        print("Closing connection...")
        break


# Close the connection.
client.close()

# Close the server socket.
server.close()