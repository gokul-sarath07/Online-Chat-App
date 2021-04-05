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
        """
        Choosing a nickname and connecting to server.
        param: nickname, type: string.
        """
        self.nickname = nickname
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(Client.ADDR)



    def receive_message(self):
        """
        Send nickname and listens for incoming messages.
        param: None.
        return: None.
        """
        while True:
            try:
                # Receive message from server.
                message = self.client.recv(Client.HEADER).decode(Client.FORMAT)
                # If message == 'NICK', Send Nickname.
                if message == 'NICK':
                    self.client.send(self.nickname.encode(Client.FORMAT))
                # else print message.
                else:
                    print(message)
            except Exception as e:
                # Close connection when error occures
                print("[EXCEPTION C-rm] ", e)
                self.client.send('{!DISCONNECT}'.encode(Client.FORMAT))
                self.client.close()
                break


    def send_message(self, message=''):
        """
        Sending Messages to Server.
        param: message, type: string.
        return: None.
        """
        while True:
            try:
                # Closes connection if message is {!DISCONNECT}
                if message == '{!DISCONNECT}':
                    self.client.send(message.encode(Client.FORMAT))
                    self.client.close()
                    break
                # Sends message to all clients.
                else:
                    if message != '':
                        msg = '{}: {}'.format(self.nickname, message)
                        self.client.send(msg.encode(Client.FORMAT))
                    else:
                        pass
            except Exception as e:
                print("[EXCEPTION C-sm] ", e)
                break


    def disconnect(self):
        """
        Disconnecting client.
        param: None.
        return: None.
        """
        self.send_message('{!DISCONNECT}')
