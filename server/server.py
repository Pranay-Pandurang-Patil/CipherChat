import socket


# IP address where our server will listen.
# 127.0.0.1 means this computer.
HOST = "127.0.0.1"

# Port used for communication.
PORT = 5000


# Create a TCP socket.
# AF_INET  = IPv4
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
# 1. A new socket for communicating with the client
# 2. The client's IP address and port
client, address = server.accept()

print("Client connected:", address)


# Receive data from the client.
# recv() receives bytes from the network.
data = client.recv(1024)


# Convert the received bytes back into normal text.
message = data.decode()

print("Client:", message)


# Close the connection after receiving the message.
client.close()
server.close()