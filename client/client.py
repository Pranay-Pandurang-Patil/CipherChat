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


# Receive the authentication option request.
data = client.recv(1024)

message = data.decode()

print(message.strip())


# Ask the user to choose REGISTER or LOGIN.
option = input("Choose: ").strip().upper()


# Send the selected option.
client.send(
    option.encode()
)


# Receive username request.
data = client.recv(1024)

message = data.decode()

print(message.strip())


# Ask for username.
username = input("Username: ").strip()


# Send username.
client.send(
    username.encode()
)


# -------------------------
# EMAIL
# -------------------------

if option == "REGISTER":

    # Receive email request.
    data = client.recv(1024)

    message = data.decode()

    print(message.strip())


    # Ask for email.
    email = input("Email: ").strip()


    # Send email.
    client.send(
        email.encode()
    )


# -------------------------
# PASSWORD
# -------------------------

# Receive password request.
data = client.recv(1024)

message = data.decode()

print(message.strip())


# Ask for password.
password = input("Password: ")


# Send password.
client.send(
    password.encode()
)


# Receive authentication result.
data = client.recv(1024)

message = data.decode()

print(message.strip())


# Check authentication.
if message.strip() != "AUTHENTICATION SUCCESS":

    print("Authentication failed.")

    client.close()


else:

    print(
        "You are now connected to CipherChat."
    )


    # -------------------------
    # RECEIVE MESSAGES
    # -------------------------

    def receive_messages():

        # Buffer for incomplete messages.
        buffer = ""


        while True:

            try:

                # Receive data from server.
                data = client.recv(1024)


                # Server closed connection.
                if data == b"":

                    print(
                        "Server disconnected."
                    )

                    break


                # Add data to buffer.
                buffer = (
                    buffer
                    + data.decode()
                )


                # Process complete messages.
                while "\n" in buffer:

                    message, buffer = (
                        buffer.split(
                            "\n",
                            1
                        )
                    )


                    # Display message.
                    print(message)


            except ConnectionResetError:

                print(
                    "Server connection was reset."
                )

                break


    # Start receiving thread.
    receive_thread = threading.Thread(
        target=receive_messages
    )

    receive_thread.start()


    # -------------------------
    # SEND MESSAGES
    # -------------------------

    while True:

        # Ask user for message.
        message = input("You: ")


        # Add message delimiter.
        message = message + "\n"


        # Convert to bytes.
        data = message.encode()


        # Send message.
        client.send(data)


        # Exit chat.
        if message.strip().lower() == "exit":

            print(
                "Closing connection..."
            )

            break


    # Close socket.
    client.close()