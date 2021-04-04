# Required Packages
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
from threading import Thread, active_count
from datetime import datetime

# GLOABL CONSTANTS
HEADER = 512
FORMAT = 'utf-8'
MAX_CONNECTIONS = 10
# HOST = gethostbyname(gethostname())
HOST = '127.0.0.1'
PORT = 55555
ADDR = (HOST, PORT)

# GLOBAL VARIABLES
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)
clients = []
nicknames = []


def broadcast(message):
    """
    Sending messages to all connected clients.
    param: message, type: string.
    return: None.
    """
    for client in clients:
        client.send(message)


def handle_client(client):
    """
    Handling messages from clients.
    param: client, type: object.
    return: None.
    """
    while True:
        try:
            # Receive message from client.
            message = client.recv(HEADER)
            # Remove client if message is {!DISCONNECT}.
            if message.decode(FORMAT) == '{!DISCONNECT}':
                remove_client(client)
                break
            # Broadcasting messages
            else:
                broadcast(message)
        except Exception as e:
            print("[EXCEPTION S-hc] ", e)
            # Removes client
            remove_client(client)
            break

def remove_client(client):
    """
    Removing and closing client.
    param: client, type: object.
    return: None.
    """
    index = clients.index(client)
    clients.remove(client)
    client.close()
    nickname = nicknames[index]
    broadcast("{} has left the chat!".format(nickname).encode(FORMAT))
    nicknames.remove(nickname)


def waiting_for_connections():
    """
    Listens for upcoming connections.
    param: None.
    return: None.
    """
    while True:
        try:
            # Accept connection.
            client, address = SERVER.accept()
            print("[NEW CONNECTION] {} connected to server at {}".format(str(address), datetime.now()))

            # Request and store nickname.
            client.send('NICK'.encode(FORMAT))
            nickname = client.recv(HEADER).decode(FORMAT)
            nicknames.append(nickname)
            clients.append(client)

            # Broadcaste join message.
            broadcast("{} joined the chat!".format(nickname).encode(FORMAT))

            # Start handling thread for client.
            thread = Thread(target=handle_client, args=(client,))
            thread.start()
            # Print number of active connections.
            print("[ACTIVE CONNECTIONS] {}".format(active_count() - 2))
        except Exception as e:
            print("[EXEPTION S-wfc] ", e)
            break
    print("SERVER CRASHED!")



if __name__ == '__main__':
    """
    Start server.
    """
    SERVER.listen(MAX_CONNECTIONS)
    print("[STARTING] server is starting...")
    print("[LISTENING] server is listening on {}".format(HOST))
    ACCEPT_CONNECTION = Thread(target=waiting_for_connections)
    ACCEPT_CONNECTION.start()
    ACCEPT_CONNECTION.join()
    SERVER.close()
