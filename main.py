from flask import Flask, render_template, url_for, redirect, request
from threading import Thread
from client import Client
from socket import gethostname, gethostbyname

app = Flask(__name__)
app.secret_key = 'secret_pass_code'


newClient = None

@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        global newClient
        client_name = request.form['form-input']
        # Create a new client.
        print("NAME RECEIVED")
        newClient = Client(client_name)
        print("NAME SEND")
        # Starting thread for receiving and sending.
        newClient.start_client_threads()
        print("THREADS CREATED")
        return redirect(url_for('chatroom'))
    return render_template('login.html')


@app.route('/chatroom')
def chatroom():
    return render_template('chat_room.html')

@app.route('/logout')
def logout():
    # name = request.args.get('client_name')
    newClient.disconnect()
    return redirect(url_for('login'))


if __name__ == '__main__':
    # host=gethostbyname(gethostname())
    app.run(debug=False)
