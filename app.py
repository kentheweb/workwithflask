from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from flask_socketio import SocketIO, join_room

app = Flask(__name__)

app.config['SECRET_KEY'] = 'LUMULI'
socketio = SocketIO(app)


@app.route('/home')
def home():
    if 'email' and 'username' in session:
        name = session['username']
        return render_template('index.html', name=name)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        session['email'] = email
        session['username'] = username
        return redirect(url_for('home'))


@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email', None) and session.pop('username', None)
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/register/group', methods=['POST'])
def register_group():
    data = request.get_json()
    app.logger.info(data)
    return make_response(jsonify({
        'message': 'group created successfully'
    }))


@app.route('/start/conversation/<name>')
def converse(name):
    details = name
    identify = session['username']
    return render_template('converse.html', details=details, identify=identify)


@app.route('/search')
def search():
    name = request.args.get('search')
    return name


@socketio.on('my event')
def check_connection(data):
    app.logger.info(data)
    socketio.emit('server', data)


@socketio.on('join room')
def done(data):
    join_room(room=data['room'])


@socketio.on('receive message')
def recvmsg(data):
    app.logger.info(data)


if __name__ == '__main__':
    socketio.run(app, port=5050, debug=True)
