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

    # Store data that has not formed a complete message yet.
    buffer = ""

    # Keep waiting for messages from the server.
    while True:

        try:

            # Receive data from the server.
            data = client.recv(1024)

            # Check if the server closed the connection.
            if data == b"":
                print("Server disconnected.")
                break

            # Add received data to the buffer.
            buffer = buffer + data.decode()

            # Process complete messages.
            while "\n" in buffer:

                # Separate one complete message.
                message, buffer = buffer.split("\n", 1)

                # Display the message.
                print(message)

        except ConnectionResetError:

            # Handle an unexpected connection close.
            print("Server connection was reset.")
            break


# Receive the username request from the server.
data = client.recv(1024)

# Convert bytes into text.
message = data.decode()

print(message.strip())


# Ask the user for a username.
username = input("Username: ")


# Send the username to the server.
client.send(username.encode())


# Start the thread for receiving messages.
receive_thread = threading.Thread(
    target=receive_messages
)

receive_thread.start()


print("Connected to CipherChat.")


# Keep asking the user for messages.
while True:

    # Ask the user for a message.
    message = input("You: ")

    # Add the message delimiter.
    message = message + "\n"

    # Convert the message into bytes.
    data = message.encode()

    # Send the message to the server.
    client.send(data)

    # Check if the user wants to exit.
    if message.strip().lower() == "exit":
        print("Closing connection...")
        break


# Close the connection.
client.close()