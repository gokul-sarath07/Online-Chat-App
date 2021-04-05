from flask import Flask, render_template, url_for, redirect, request
from threading import Thread
from client import Client
from socket import gethostname, gethostbyname

app = Flask(__name__)
app.secret_key = 'secret_pass_code'


newClient = None

@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/chatroom', methods=['POST', 'GET'])
def chatroom():
    if request.method == 'POST':
        global newClient
        client_name = request.form['form-input']
        # Create a new client.
        newClient = Client(client_name)
        # Starting Threads for Listening.
        Thread(target=newClient.receive_message).start()
        Thread(target=newClient.send_message).start()
        return render_template('chat_room.html')

@app.route('/logout')
def logout():
    # name = request.args.get('client_name')
    newClient.disconnect()
    return redirect(url_for('login'))


if __name__ == '__main__':
    # host=gethostbyname(gethostname())
    app.run(debug=False)
