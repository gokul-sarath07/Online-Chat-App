from flask import Flask, render_template, url_for, redirect, request
from threading import Thread
from client import Client
from socket import gethostname, gethostbyname

app = Flask(__name__)
app.secret_key = 'secret_pass_code'
messages = []
clients = []

newClient = None

@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        global newClient
        client_name = request.form['form-input']
        clients.append(client_name)
        # Create a new client.
        newClient = Client(client_name)
        # Starting thread for receiving and sending.
        newClient.start_client_threads()
        return redirect(url_for('chatroom'))
    return render_template('login.html')


@app.route('/chatroom', methods=['POST', 'GET'])
def chatroom():
    if request.method == 'POST':
        message = request.form['msg-input-box']
        if message != '':
            message = clients[0] + ": " + message
            messages.append(message)
            return redirect(url_for('chatroom'))
        else:
            return render_template('chat_room.html', messages=messages, clients=clients)
    else:
        return render_template('chat_room.html', messages=messages, clients=clients)


@app.route('/logout')
def logout():
    # name = request.args.get('client_name')
    newClient.disconnect()
    return redirect(url_for('login'))


@app.route('/send_message', methods=['POST'])
def send_messages():
    msg = request.args.get('val')
    print(msg)


if __name__ == '__main__':
    # host=gethostbyname(gethostname())
    app.run(debug=False)
