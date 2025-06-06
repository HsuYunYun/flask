# 匯入 Flask 相關模組與 SocketIO
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, send, emit

# 建立 Flask 應用程式實例
app = Flask(__name__)
# 設定密鑰，用於 session 等安全性用途
app.config['SECRET_KEY'] = 'chatroom123'
# 初始化 SocketIO，讓 Flask 支援即時通訊
socketio = SocketIO(app)

# 用來儲存所有訊息的列表
messages = []
# 訊息編號計數器，確保每則訊息有唯一 id
msg_counter = 0

# 登入頁面路由，支援 GET 與 POST 方法
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 如果是表單送出（POST）
    if request.method == 'POST':
        username = request.form.get('username')  # 取得使用者名稱
        if username:
            session['username'] = username      # 將使用者名稱存入 session
            return redirect(url_for('index'))   # 登入成功導向首頁
        else:
            # 沒有輸入名稱則顯示錯誤訊息
            return render_template('login.html', error='請輸入使用者名稱')
    # GET 方法顯示登入頁面
    return render_template('login.html')

# 首頁路由，需先登入才能進入
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))  # 未登入則導向登入頁
    return render_template('index.html', username=session['username'])  # 傳遞使用者名稱給模板

# 監聽 'message' 事件，處理收到的訊息
@socketio.on('message')
def handle_message(data):
    global msg_counter
    msg_counter += 1  # 訊息編號遞增
    msg = {'id': msg_counter, 'text': data['text']}  # 建立訊息物件
    messages.append(msg)  # 加入訊息列表
    emit('message', msg, broadcast=True)  # 廣播訊息給所有用戶端

# 監聽 'delete_message' 事件，處理刪除訊息
@socketio.on('delete_message')
def handle_delete_message(msg_id):
    global messages
    # 移除指定 id 的訊息
    messages = [m for m in messages if m['id'] != msg_id]
    emit('delete_message', msg_id, broadcast=True)  # 廣播刪除事件給所有用戶端

# 程式進入點，啟動伺服器
if __name__ == '__main__':
    socketio.run(app, debug=True)
