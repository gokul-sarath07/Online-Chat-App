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
ENCODE_FORMAT = 'utf-8'

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

#  Send Nickname and Listens for Incoming Messages.
def receive_message():
    while True:
        try:
            # Receive Message from Server
            # If 'NICK' Send Nickname
            message = client.recv(HEADER).decode(ENCODE_FORMAT)
            if message == 'NICK':
                client.send(nickname.encode(ENCODE_FORMAT))
            else:
                print(message)
        except Exception as e:
            # Close Connection When Error Occures
            print("[EXCEPTION] ", e)
            client.close()
            break

# Sending Messages to Server
def send_message():
    while True:
        message = '{}: {}'.format(nickname, input(''))
        client.send(message.encode(ENCODE_FORMAT))

# Starting Threads for Listening and Writing
receive_thread = threading.Thread(target=receive_message)
receive_thread.start()

send_thread = threading.Thread(target=send_message)
send_thread.start()
