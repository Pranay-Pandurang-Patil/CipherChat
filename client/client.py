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

# Ask the user for a message.
message = input("You: ")

# Convert the text into bytes.
# Sockets send bytes, not normal Python strings.
data = message.encode()


# Send the message to the server.
client.send(data)

print("Message sent.")


# Close the connection.
client.close()