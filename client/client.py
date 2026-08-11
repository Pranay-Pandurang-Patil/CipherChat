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

    # Ask the user for a message.
    message = input("You: ")

    # Convert the message into bytes.
    data = message.encode()

    # Send the message to the server.
    client.send(data)

    # If the user wants to exit, stop after notifying the server.
    if message.lower() == "exit":
        print("Closing connection...")
        break

    # Wait for the server's reply.
    data = client.recv(1024)

    # Convert the reply from bytes into text.
    reply = data.decode()

    print("Server:", reply)


# Close the connection.
client.close()