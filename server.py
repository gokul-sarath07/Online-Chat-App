# Required Packages
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
from threading import Thread, active_count
from datetime import datetime

# Constants
HEADER = 512
FORMAT = 'utf-8'
MAX_CONNECTIONS = 10

# Connection Data
HOST = gethostbyname(gethostname())
# HOST = '127.0.0.1'
PORT = 55555
ADDR = (HOST, PORT)

# Starting Server
server = socket(AF_INET, SOCK_STREAM)
server.bind(ADDR)

# Lists for Clients and their Nicknames
clients = []
nicknames = []

# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Handling Messages from Clients
def handle_client(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(HEADER)
            if message.decode(FORMAT) == '{!DISCONNECT}':
                remove_client(client)
                break
            else:
                broadcast(message)
        except Exception as e:
            print("[EXCEPTION] ", e)
            # Removes Client
            remove_client(client)
            break

def remove_client(client):
    # Removing and Closing Client
    index = clients.index(client)
    clients.remove(client)
    client.close()
    nickname = nicknames[index]
    broadcast("{} has left the chat!".format(nickname).encode(FORMAT))
    nicknames.remove(nickname)

# Listening Function
def waiting_for_connections():
    while True:
        try:
            # Accept Connection
            client, address = server.accept()
            print("[NEW CONNECTION] {} connected to server at {}".format(str(address), datetime.now()))

            # Request and Store Nickname
            client.send('NICK'.encode(FORMAT))
            nickname = client.recv(HEADER).decode(FORMAT)
            nicknames.append(nickname)
            clients.append(client)

            # Print and Broadcast Nickname
            broadcast("{} joined the chat!".format(nickname).encode(FORMAT))

            # Start Handling thread for Client
            thread = Thread(target=handle_client, args=(client,))
            thread.start()
            print("[ACTIVE CONNECTIONS] {}".format(active_count() - 1))
        except Exception as e:
            print("[EXEPTION] ", e)
            break
    print("SERVER CRASHED!")


# Start Server
if __name__ == '__main__':
    server.listen(MAX_CONNECTIONS)
    print("[STARTING] server is starting...")
    print("[LISTENING] server is listening on {}".format(HOST))
    waiting_for_connections()
