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
client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)


# Connect to the server.
client.connect(
    (HOST, PORT)
)


# -------------------------
# AUTHENTICATION
# -------------------------

# Receive authentication option request.
data = client.recv(1024)

print(data.decode().strip())


# Ask user to choose REGISTER or LOGIN.
option = input("Choose: ").strip().upper()


# Send option to server.
client.send(option.encode())


# Receive username request.
data = client.recv(1024)

print(data.decode().strip())


# Ask for username.
username = input("Username: ").strip()


# Send username.
client.send(username.encode())


# -------------------------
# EMAIL
# -------------------------

if option == "REGISTER":

    # Receive email request.
    data = client.recv(1024)

    print(data.decode().strip())


    # Ask for email.
    email = input("Email: ").strip()


    # Send email.
    client.send(email.encode())


# -------------------------
# PASSWORD
# -------------------------

# Receive password request.
data = client.recv(1024)

print(data.decode().strip())


# Ask for password.
password = input("Password: ")


# Send password.
client.send(password.encode())


# Receive authentication result.
data = client.recv(1024)

message = data.decode().strip()


print(message)


# -------------------------
# AUTHENTICATION CHECK
# -------------------------

if message != "AUTHENTICATION SUCCESS":

    print("Authentication failed.")

    client.close()


else:

    print(
        "You are now connected to CipherChat."
    )


    # -------------------------
    # RECEIVE HISTORY
    # -------------------------

    # The server sends the message history
    # immediately after authentication.
    #
    # We receive the history BEFORE starting
    # the background receiving thread.

    history = ""

    while True:

        # Receive data from the server.
        data = client.recv(1024)


        # Server disconnected.
        if data == b"":

            print("Server disconnected.")

            client.close()

            break


        # Add received data to our buffer.
        history = history + data.decode()


        # Process complete lines.
        while "\n" in history:

            line, history = history.split(
                "\n",
                1
            )


            # Display the line.
            print(line)


            # Stop when history is finished.
            if line == "--- End of History ---":

                break


        # Check if the history ended.
        if line == "--- End of History ---":

            break


    # -------------------------
    # RECEIVE NEW MESSAGES
    # -------------------------

    def receive_messages():

        # Buffer for incoming data.
        buffer = ""


        while True:

            try:

                # Receive data from the server.
                data = client.recv(1024)


                # Server disconnected.
                if data == b"":

                    print(
                        "Server disconnected."
                    )

                    break


                # Add data to the buffer.
                buffer = buffer + data.decode()


                # Process complete messages.
                while "\n" in buffer:

                    message, buffer = (
                        buffer.split(
                            "\n",
                            1
                        )
                    )


                    # Display received message.
                    print(message)


            except ConnectionResetError:

                print(
                    "Server connection was reset."
                )

                break


    # Create receiving thread.
    receive_thread = threading.Thread(
        target=receive_messages
    )


    # Start receiving thread.
    receive_thread.start()


    # -------------------------
    # SEND MESSAGES
    # -------------------------

    while True:

        # Ask user for a message.
        message = input("You: ")


        # Add newline delimiter.
        message = message + "\n"


        # Convert message to bytes.
        data = message.encode()


        # Send message.
        client.send(data)


        # Check for exit.
        if message.strip().lower() == "exit":

            print(
                "Closing connection..."
            )

            break


    # Close the connection.
    client.close()