# Required Packages
import socket
import threading

# Choosing Nickname
nickname = input("Choose your nickname: ")

# Constants
HOST = socket.gethostbyname(socket.gethostname())
# HOST = '127.0.0.1'
PORT = 55555
ADDR = (HOST, PORT)
HEADER = 512
FORMAT = 'utf-8'

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


#  Send Nickname and Listens for Incoming Messages.
def receive_message():
    while True:
        try:
            # Receive Message from Server
            # If 'NICK' Send Nickname
            message = client.recv(HEADER).decode(FORMAT)
            if message == 'NICK':
                client.send(nickname.encode(FORMAT))
            else:
                print(message)
        except Exception as e:
            # Close Connection When Error Occures
            print("[EXCEPTION] ", e)
            client.close()
            break


# Sending Messages to Server
def send_message(message=None):
    while True:
        if message == '{!DISCONNECT}':
            client.close()
            break
        else:
            message = '{}: {}'.format(nickname, input(''))
            client.send(message.encode(FORMAT))


# Disconnecting Client
def disconnect():
    send_message('{!DISCONNECT}')


# Starting Threads for Listening and Writing
receive_thread = threading.Thread(target=receive_message)
receive_thread.start()

send_thread = threading.Thread(target=send_message)
send_thread.start()
