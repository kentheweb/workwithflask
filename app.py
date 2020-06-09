from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response, flash
from flask_socketio import SocketIO, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

app = Flask(__name__)

app.config['SECRET_KEY'] = 'LUMULI'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True

socketio = SocketIO(app)
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    hash = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return 'name %s' % self.name


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.Integer)
    sender = db.Column(db.String(250), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return 'name %s' % self.id


def generate_hash(email):
    url = hashlib.md5(str(email).encode('utf-8')).hexdigest()
    return url


@app.route('/home')
def home():
    if 'email' and 'username' in session:
        user = User.query.filter_by().all()
        name = session['username']
        return render_template('index.html', name=name, user=user)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password=password):
                session['email'] = email
                session['username'] = user.name
                return redirect(url_for('home'))
            else:
                flash('wrong password the field may be too sensitive', 'danger')
                return redirect(url_for('login'))
        else:
            flash('please create an account before login in', 'danger')
            return redirect(url_for('register'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        hash = generate_hash(email=email)
        password = request.form.get('password')
        passw = generate_password_hash(password=password, method='sha256')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('the email entered already exists please choose a different one', 'danger')
            return redirect(url_for('register'))
        user = User(name=name, email=email, password=passw, hash=hash)
        db.session.add(user)
        db.session.commit()
        flash('account created successfully', 'success')
        return redirect(url_for('login'))
    else:
        return render_template('register.html')


@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email', None) and session.pop('username', None)
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/start/conversation/<int:id>')
def converse(id):
    user = User.query.get_or_404(id)
    details = user.name
    identify = session['username']
    user = User.query.filter_by(name=identify).first()
    msg = Messages.query.filter_by().all()
    return render_template('converse.html', details=details, user=user, msg=msg)


@app.route('/account')
def account():
    if 'email in session':
        user = session['email']
        client = User.query.filter_by(email=user).first()
        return render_template('account.html', client=client)

    return redirect(url_for('login'))


@socketio.on('my event')
def check_connection(data):
    join_room(data['room'])
    socketio.emit('server', data, room=data['room'])


@socketio.on('receive message')
def handle_message(data):
    app.logger.debug(data)
    msg = data['message']
    sender = data['sender']
    room = data['room']
    item = Messages(sender=sender, message=msg, room=room)
    db.session.add(item)
    db.session.commit()
    socketio.emit('receive', data)


if __name__ == '__main__':
    socketio.run(app, port=5050, debug=True)
