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


# Receive the authentication option request.
data = client.recv(1024)

# Convert bytes into text.
message = data.decode()

print(message.strip())


# Ask the user to choose REGISTER or LOGIN.
option = input("Choose: ").strip().upper()


# Send the selected option to the server.
client.send(option.encode())


# Receive the username request.
data = client.recv(1024)

# Convert bytes into text.
message = data.decode()

print(message.strip())


# Ask for username.
username = input("Username: ").strip()


# Send the username.
client.send(username.encode())


# Receive the password request.
data = client.recv(1024)

# Convert bytes into text.
message = data.decode()

print(message.strip())


# Ask for password.
password = input("Password: ")


# Send the password.
client.send(password.encode())


# Receive the authentication result.
data = client.recv(1024)

# Convert bytes into text.
message = data.decode()

print(message.strip())


# Check whether authentication succeeded.
if message.strip() != "AUTHENTICATION SUCCESS":

    # Authentication failed.
    print("Authentication failed.")
    client.close()

else:

    print("You are now connected to CipherChat.")


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

                # Handle unexpected connection close.
                print("Server connection was reset.")
                break


    # Start the receiving thread.
    receive_thread = threading.Thread(
        target=receive_messages
    )

    receive_thread.start()


    # Keep asking the user for messages.
    while True:

        # Ask for a message.
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