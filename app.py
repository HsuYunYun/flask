
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chatroom'
socketio = SocketIO(app)

messages = []
msg_counter = 0

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            session['username'] = username      
            return redirect(url_for('index'))   
        else:
            return render_template('login.html', error='請輸入使用者名稱')
    return render_template('login.html')

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@socketio.on('message')
def handle_message(data):
    global msg_counter
    msg_counter += 1 
    msg = {'id': msg_counter, 'text': data['text']}
    messages.append(msg)
    emit('message', msg, broadcast=True)

@socketio.on('delete_message')
def handle_delete_message(msg_id):
    global messages
    messages = [m for m in messages if m['id'] != msg_id]
    emit('delete_message', msg_id, broadcast=True) 

if __name__ == '__main__':
    socketio.run(app, debug=True)
