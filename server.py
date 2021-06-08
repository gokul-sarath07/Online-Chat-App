from datetime import datetime
from bson.json_util import dumps
from flask import Flask, render_template, url_for, redirect, request
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from pymongo.errors import DuplicateKeyError

from db import get_user, save_user, save_room, add_room_members, \
	get_rooms_for_user, get_room, is_room_member, get_room_members, is_room_admin, \
	remove_room_members, update_room, save_message, get_messages


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_pass_code'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@app.route('/home')
@login_required
def home():
	rooms = []
	if current_user.is_authenticated:
		rooms = get_rooms_for_user(current_user.username)
	return render_template('home.html', rooms=rooms)


@app.route('/', methods=['GET', 'POST'])
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


@app.route('/create-room', methods=['GET', 'POST'])
@login_required
def create_room():
	message = ''
	if request.method == 'POST':
		room_name = request.form.get('room_name')
		usernames = [username.strip() for username in request.form.get('members').split(',')]
		rooms = get_rooms_for_user(current_user.username)
		rooms = [rooms[idx]["room_name"] for idx in range(len(rooms))]
		rooms.append('')
		if room_name not in rooms and usernames != ['']:
			room_id = save_room(room_name, current_user.username)
			if current_user.username in usernames:
				usernames.remove(current_user.username)
			if usernames != []:
				add_room_members(room_id, room_name, usernames, current_user.username)
			return redirect(url_for('chat_room', room_id=room_id))
		else:
			message = 'Room creation failed!'
	return render_template('create_room.html', message=message)


@app.route('/rooms/<room_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
	room = get_room(room_id)
	if room and is_room_admin(room_id, current_user.username):
		existing_room_members = [member['_id']['username'] for member in get_room_members(room_id)]
		room_members_str = ",".join(existing_room_members)
		message = ''

		if request.method == 'POST':
			room_name = request.form.get('room_name')
			room['room_name'] = room_name
			update_room(room_id, room_name)

			new_members = [username.strip() for username in request.form.get('members').split(',')]
			members_to_add = list(set(new_members) - set(existing_room_members))
			members_to_remove = list(set(existing_room_members) - set(new_members))
			if members_to_add != []:
				add_room_members(room_id, room_name, members_to_add, current_user.username)
			if members_to_remove != []:
				remove_room_members(room_id, members_to_remove)
			message = 'Room Edited Successfully!'
			room_members_str = ",".join(new_members)
		return render_template('edit_room.html', room=room, room_members_str=room_members_str, message=message)
	else:
		return "Room not found!", 404


@app.route('/rooms/<room_id>/')
@login_required
def chat_room(room_id):
	room = get_room(room_id)
	if room and is_room_member(room_id, current_user.username):
		is_admin = is_room_admin(room_id, current_user.username)
		room_members = get_room_members(room_id)
		messages = get_messages(room_id)
		return render_template('chat_room.html', username=current_user.username,
			room=room, room_members=room_members, messages=messages, is_admin=is_admin)
	else:
		return "Room not found!", 404


@app.route('/rooms/<room_id>/history/')
@login_required
def get_older_messages(room_id):
	room = get_room(room_id)
	if room and is_room_member(room_id, current_user.username):
		page = int(request.args.get('page', 0))
		messages = get_messages(room_id, page)
		return dumps(messages)
	else:
		return "Room not found!", 404


@socketio.on('send_message')
def send_message_event(data):
	app.logger.info('{} has send message to room {}: {}.'.format(data['username'],
																 data['room'],
																 data['message']))
	data['send_time'] = datetime.now().strftime("%d-%b-%Y, %H:%M:%S")
	save_message(data['room'], data['message'], data['username'])
	socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def join_room_event(data):
	if data['username']:
		app.logger.info('{} has joined the room {}.'.format(data['username'], data['room']))
		join_room(data['room'])
		socketio.emit('join_room_announcement', data, room=data['room'])


@socketio.on('leave_room')
def leave_room_event(data):
	if data["username"]:
		app.logger.info("{} has left the room {}.".format(data["username"], data['room']))
		leave_room(data['room'])
		socketio.emit('leave_room_announcement', data, room=data['room'])


@login_manager.user_loader
def load_user(username):
    return get_user(username)


if __name__ == '__main__':
	socketio.run(app, debug=False)
