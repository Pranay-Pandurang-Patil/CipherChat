import socket
import threading


# IP address of the computer where our server is running.
# 127.0.0.1 means our own computer.
HOST = "127.0.0.1"

# This must match the server's port.
PORT = 5000


# Create a TCP socket.
# AF_INET = IPv4
# SOCK_STREAM = TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Connect to the server.
client.connect((HOST, PORT))


def receive_messages():

    # Keep waiting for messages from the server.
    while True:

        # Receive data from the server.
        data = client.recv(1024)

        # Convert the received bytes into text.
        message = data.decode()

        # Display the server's message.
        print("Server:", message)


# Create a thread for receiving messages.
receive_thread = threading.Thread(target=receive_messages)

# Start the receiving thread.
receive_thread.start()


print("Connected to CipherChat server.")


# Main program is used for sending messages.
while True:

    # Ask the user for a message.
    message = input("You: ")

    # Convert the message into bytes.
    data = message.encode()

    # Send the message to the server.
    client.send(data)

    # Check if the user wants to exit.
    if message.lower() == "exit":
        print("Closing connection...")
        break


# Close the connection.
client.close()