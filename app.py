from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from flask_socketio import SocketIO, join_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

app = Flask(__name__)


app.config['SECRET_KEY'] = 'LUMULI'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True

socketio = SocketIO(app)
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    hash = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return 'name %s' % self.name


def generate_hash(email):
    url = hashlib.md5(email).hexdigest()
    return url


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
    join_room(data['message'])
    socketio.emit('server', data)


@socketio.on('receive message')
def handle_message(data):
    app.logger.debug(data)
    socketio.emit('receive', data)


if __name__ == '__main__':
    socketio.run(app, port=5050, debug=True)
