# from flask import Flask,render_template,request, jsonify

# app = Flask(__name__)

# @app.route("/")
# def hello():
#     return render_template('index.html')

# @app.route("/uppercase", methods=['POST'])
# def uppercase():
#     data = request.json
#     text = data.get('text', '')
#     return jsonify({'text': text.upper()})

# if __name__ == "__main__":
#     import webbrowser
#     import threading
#     import os

#     def _open_browser():
#         webbrowser.open_new("http://127.0.0.1:5000/")

#     # When using the reloader, the process runs twice. Only open browser
#     # in the child process (WERKZEUG_RUN_MAIN == "true").
#     if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
#         threading.Timer(1.0, _open_browser).start()

#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# 初始化数据库
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()

# 获取数据库连接
def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 避免 SQL 注入，使用参数化查询
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 避免 SQL 注入，使用参数化查询
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()

        if user:
            return redirect(url_for('dashboard'))
        else:
            return "登录失败！", 401

    return render_template('login.html')

# 登录成功后的页面
@app.route('/dashboard')
def dashboard():
    return "欢迎来到仪表盘!"

# 主页
@app.route('/')
def home():
    return redirect(url_for('register'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

