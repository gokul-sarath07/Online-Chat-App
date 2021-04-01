# Required Packages
import socket
import threading

# Constants
HEADER = 512
ENCODE_FORMAT = 'utf-8'

# Connection Data
HOST = socket.gethostbyname(socket.gethostname())
# HOST = '127.0.0.1'
PORT = 55555
ADDR = (HOST, PORT)

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Lists for Clients and their Nicknames
clients = []
nicknames = []

# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Handling Messages from Clients
def handle_messages(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(HEADER)
            broadcast(message)
        except Exception as e:
            print("[EXCEPTION] ", e)

            # Removing and Closing Client
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast("{} has left the chat!".format(nickname).encode(ENCODE_FORMAT))
            nicknames.remove(nickname)
            break

# Listening Function
def start_server():
    server.listen()
    print("[LISTENING] server is listening on {}".format(HOST))
    while True:
        # Accept Connection
        client, address = server.accept()
        print("[NEW CONNECTION] {} connected".format(str(address)))

        # Request and Store Nickname
        client.send('NICK'.encode(ENCODE_FORMAT))
        nickname = client.recv(HEADER).decode(ENCODE_FORMAT)
        nicknames.append(nickname)
        clients.append(client)

        # Print and Broadcast Nickname
        broadcast("{} joined the chat!".format(nickname).encode(ENCODE_FORMAT))

        # Start Handling thread for Client
        thread = threading.Thread(target=handle_messages, args=(client,))
        thread.start()
        print("[ACTIVE CONNECTIONS] {}".format(threading.active_count() - 1))


# Start Server
print("[STARTING] server is starting...")
start_server()
