# Required Packages
import socket
# import threading

class Client:

    # GLOBAL CONSTANTS
    # HOST = socket.gethostbyname(socket.gethostname())
    HOST = '127.0.0.1'
    PORT = 55555
    ADDR = (HOST, PORT)
    HEADER = 512
    FORMAT = 'utf-8'

    def __init__(self, nickname):
        # Choosing Nickname
        self.nickname = nickname
        # Connecting To Server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(Client.ADDR)


    #  Send Nickname and Listens for Incoming Messages.
    def receive_message(self):
        while True:
            try:
                # Receive Message from Server
                # If 'NICK' Send Nickname
                message = self.client.recv(Client.HEADER).decode(Client.FORMAT)
                if message == 'NICK':
                    self.client.send(self.nickname.encode(Client.FORMAT))
                else:
                    print(message)
            except Exception as e:
                # Close Connection When Error Occures
                print("[EXCEPTION C-re] ", e)
                self.client.send('{!DISCONNECT}'.encode(Client.FORMAT))
                self.client.close()
                break


    # Sending Messages to Server
    def send_message(self, message=''):
        while True:
            try:
                if message == '{!DISCONNECT}':
                    self.client.send(message.encode(Client.FORMAT))
                    self.client.close()
                    break
                else:
                    msg = '{}: {}'.format(self.nickname, message)
                    self.client.send(msg.encode(Client.FORMAT))
            except Exception as e:
                print("[EXCEPTION C-sm] ", e)


    # Disconnecting Client
    def disconnect(self):
        self.send_message('{!DISCONNECT}')


# Starting Threads for Listening and Writing
# receive_thread = threading.Thread(target=receive_message)
# receive_thread.start()

# send_thread = threading.Thread(target=send_message)
# send_thread.start()
