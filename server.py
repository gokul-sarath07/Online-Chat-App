from flask import Flask, render_template, url_for, redirect, request
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from db import get_user, save_user
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_pass_code'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@app.route('/')
def home():
	return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	message = ''
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		user_object = get_user(username)
		if user_object and user_object.check_password(password):
			login_user(user_object)
			return redirect(url_for('home'))
		else:
			message = 'Login Failed!'
	return render_template('login.html', message=message)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	message = ''
	if request.method == 'POST':
		username = request.form.get('username')
		email = request.form.get('email')
		password = request.form.get('password')
		user_object = get_user(username)
		try:
			save_user(username, email, password)
			return redirect(url_for('login'))
		except DuplicateKeyError:
			message = 'User already exists!'
	return render_template('signup.html', message=message)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/chatroom')
@login_required
def chatroom():
	username = request.args.get('username')
	room_number = request.args.get('room-number')
	if username and room_number:
		return render_template('chat_room.html', username=username, room_number=room_number)
	else:
		return redirect(url_for('home'))


@socketio.on('send_message')
def send_message_event(data):
	app.logger.info('{} has send message to room {}: {}.'.format(data['username'],
																 data['room_number'],
																 data['message']))
	socketio.emit('receive_message', data, room=data['room_number'])

@socketio.on('disconnect_user')
def disconnect(data):
	if data["username"] != '':
		app.logger.info("{} has left the server.".format(data["username"]))
		socketio.emit('leave_chat_announcement', data, broadcast=True)

@socketio.on('join_room')
def join_room_event(data):
	if data['username']:
		app.logger.info('{} has joined the room {}.'.format(data['username'], data['room_number']))
		join_room(data['room_number'])
		socketio.emit('join_room_announcement', data, broadcast=True)

@login_manager.user_loader
def load_user(username):
    return get_user(username)

if __name__ == '__main__':
	socketio.run(app, debug=True)
