from flask import Flask, render_template, url_for, redirect, request
from flask_socketio import SocketIO, send, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_pass_code'
socketio = SocketIO(app)

@app.route('/')
@app.route('/login', methods=['POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		return redirect(url_for('chatroom', username=username))
	else:
		return render_template('login.html')

@app.route('/chatroom')
def chatroom():
	username = request.args.get('username')
	return render_template('chat_room.html', username=username)

@socketio.on('send_message')
def send_message(data):
	app.logger.info('{} has send message: {}.'.format(data['username'], data['message']))
	socketio.emit('receive_message', data)


@socketio.on('connect_info')
def connect_info(data):
	if data["username"] != '':
		app.logger.info('{} has joined the server.'.format(data['username']))
		socketio.emit('make_chat_announcement', data, broadcast=True)

if __name__ == '__main__':
	socketio.run(app, debug=True)
