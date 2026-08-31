import socket
import threading


# =========================================================
# SERVER SETTINGS
# =========================================================

HOST = "127.0.0.1"
PORT = 5000


# =========================================================
# CREATE SOCKET
# =========================================================

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)


# Connect to server.
client.connect(
    (HOST, PORT)
)


# =========================================================
# RECEIVE BUFFER
# =========================================================

# TCP is a continuous stream.
# One recv() does not necessarily contain
# exactly one message.
buffer = ""


def receive_line():

    global buffer


    # Keep receiving until we get a complete line.
    while "\n" not in buffer:

        data = client.recv(1024)


        # Server disconnected.
        if data == b"":

            return None


        # Decode safely.
        buffer = (
            buffer
            + data.decode(
                "utf-8",
                errors="replace"
            )
        )


    # Extract one complete message.
    message, buffer = (
        buffer.split(
            "\n",
            1
        )
    )


    return message


def send_message(message):

    # Add newline delimiter.
    message = message + "\n"


    # Encode using UTF-8.
    data = message.encode(
        "utf-8"
    )


    # Send to server.
    client.send(data)


# =========================================================
# AUTHENTICATION
# =========================================================

message = receive_line()

if message is None:

    print("Server disconnected.")

    client.close()

    exit()


print(message)


# Choose REGISTER or LOGIN.
option = input(
    "Choose: "
).strip().upper()


send_message(option)


# =========================================================
# USERNAME
# =========================================================

message = receive_line()

if message is None:

    print("Server disconnected.")

    client.close()

    exit()


print(message)


username = input(
    "Username: "
).strip()


send_message(username)


# =========================================================
# EMAIL
# =========================================================

if option == "REGISTER":

    message = receive_line()


    if message is None:

        print("Server disconnected.")

        client.close()

        exit()


    print(message)


    email = input(
        "Email: "
    ).strip()


    send_message(email)


# =========================================================
# PASSWORD
# =========================================================

message = receive_line()


if message is None:

    print("Server disconnected.")

    client.close()

    exit()


print(message)


password = input(
    "Password: "
)


send_message(password)


# =========================================================
# AUTHENTICATION RESULT
# =========================================================

message = receive_line()


if message is None:

    print("Server disconnected.")

    client.close()

    exit()


print(message)


# Authentication failed.
if message != "AUTHENTICATION SUCCESS":

    print(
        "Authentication failed."
    )

    client.close()

    exit()


print(
    "You are now connected to CipherChat."
)


# =========================================================
# ROOM MENU
# =========================================================

message = receive_line()


if message is None:

    print("Server disconnected.")

    client.close()

    exit()


print(message)


room_option = input(
    "Choose: "
).strip().upper()


send_message(room_option)


# =========================================================
# CREATE ROOM
# =========================================================

if room_option == "CREATE":

    message = receive_line()


    if message is None:

        print("Server disconnected.")

        client.close()

        exit()


    print(message)


    room_name = input(
        "Room name: "
    ).strip()


    send_message(room_name)


# =========================================================
# JOIN ROOM
# =========================================================

elif room_option == "JOIN":

    message = receive_line()


    if message is None:

        print("Server disconnected.")

        client.close()

        exit()


    print(message)


    room_code = input(
        "Room code: "
    ).strip()


    send_message(room_code)


else:

    print(
        "Invalid room option."
    )

    client.close()

    exit()


# =========================================================
# ROOM RESULT
# =========================================================

message = receive_line()


if message is None:

    print("Server disconnected.")

    client.close()

    exit()


print(message)


if (
    message == "Room creation failed."
    or message == "Unable to join room."
    or message == "Invalid room code."
):

    print(
        "Room operation failed."
    )

    client.close()

    exit()


# =========================================================
# ROOM INFORMATION
# =========================================================

while True:

    message = receive_line()


    if message is None:

        print(
            "Server disconnected."
        )

        client.close()

        exit()


    print(message)


    if message == "--- End Members ---":

        break


# =========================================================
# ROOM MESSAGE HISTORY
# =========================================================

while True:

    message = receive_line()


    if message is None:

        print(
            "Server disconnected."
        )

        client.close()

        exit()


    print(message)


    if message == "--- End of History ---":

        break


# =========================================================
# RECEIVE NEW MESSAGES
# =========================================================

def receive_messages():

    global buffer


    while True:

        try:

            data = client.recv(1024)


            # Server disconnected.
            if data == b"":

                print(
                    "\nServer disconnected."
                )

                break


            # Decode safely.
            buffer = (
                buffer
                + data.decode(
                    "utf-8",
                    errors="replace"
                )
            )


            # Process every complete message.
            while "\n" in buffer:

                message, buffer = (
                    buffer.split(
                        "\n",
                        1
                    )
                )


                print(
                    "\n" + message
                )


        except ConnectionResetError:

            print(
                "\nServer connection was reset."
            )

            break


        except OSError:

            break


# =========================================================
# START RECEIVE THREAD
# =========================================================

receive_thread = threading.Thread(
    target=receive_messages,
    daemon=True
)


receive_thread.start()


# =========================================================
# CHAT INPUT
# =========================================================

print(
    "\nYou are now in the chat."
)

print(
    "Type a message and press Enter."
)

print(
    "Type 'exit' to leave."
)


while True:

    try:

        message = input(
            "You: "
        )


        # Add message delimiter.
        send_message(message)


        # Exit chat.
        if message.lower() == "exit":

            print(
                "Closing connection..."
            )

            break


    except (
        ConnectionResetError,
        BrokenPipeError
    ):

        print(
            "Connection to server lost."
        )

        break


    except EOFError:

        break


# =========================================================
# CLOSE CONNECTION
# =========================================================

client.close()