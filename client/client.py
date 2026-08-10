import socket


# IP address of the computer where our server is running.
# 127.0.0.1 means our own computer.
HOST = "127.0.0.1"

# This must match the server's port.
PORT = 5000


# Create a TCP socket.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Connect to the server.
client.connect((HOST, PORT))

print("Connected to CipherChat server.")

# Keep asking the user for messages.
while True:

    # Ask the user to type a message.
    message = input("You: ")

    # Check if the user wants to leave the chat.
    if message.lower() == "exit":
        print("Closing connection...")
        break

    # Convert the text into bytes.
    data = message.encode()

    # Send the message to the server.
    client.send(data)

    print("Message sent.")


# Close the connection after leaving the loop.
client.close()