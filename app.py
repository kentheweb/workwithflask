from flask import Flask, render_template, request, redirect, url_for, session
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


@socketio.on('handle')
def check_connection():
    pass


@socketio.on('done')
def done():
    pass


if __name__ == '__main__':
    socketio.run(app, port=5050, debug=True)
