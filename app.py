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


# from flask import Flask, render_template, request, redirect, url_for
# import sqlite3

# app = Flask(__name__)

# # 初始化数据库
# def init_db():
#     conn = get_db()
#     cursor = conn.cursor()
#     # 创建用户表
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT NOT NULL UNIQUE,
#             password TEXT NOT NULL
#         )
#     ''')
#     conn.commit()

# # 获取数据库连接
# def get_db():
#     conn = sqlite3.connect('users.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# # 用户注册
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         # 避免 SQL 注入，使用参数化查询
#         conn = get_db()
#         cursor = conn.cursor()
#         cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
#         conn.commit()

#         return redirect(url_for('login'))

#     return render_template('register.html')

# # 用户登录
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         # 避免 SQL 注入，使用参数化查询
#         conn = get_db()
#         cursor = conn.cursor()
#         cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
#         user = cursor.fetchone()

#         if user:
#             return redirect(url_for('dashboard'))
#         else:
#             return "登录失败！", 401

#     return render_template('login.html')

# # 登录成功后的页面
# @app.route('/dashboard')
# def dashboard():
#     return "欢迎来到仪表盘!"

# # 主页
# @app.route('/')
# def home():
#     return redirect(url_for('register'))

# if __name__ == '__main__':
#     init_db()
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from openai import OpenAI  # 导入 OpenAI SDK
import os  # 导入 os 模块以使用环境变量

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于 session 的加密

# 初始化数据库
def init_db():
    conn = get_db()
    cursor = conn.cursor()
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
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "用户名已存在！", 400

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
            session['username'] = user['username']  # 将用户名存入 session
            return redirect(url_for('dashboard'))
        else:
            return "登录失败！", 401

    return render_template('login.html')

# 登录成功后的页面
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))

# 聊天功能
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_input = request.form['user_input']
        try:
            response = get_chat_response(user_input)
            return render_template('chat.html', user_input=user_input, response=response)
        except Exception as e:
            return f"聊天失败: {str(e)}", 500

    return render_template('chat.html')

# 获取聊天响应
def get_chat_response(user_input):
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise Exception('OPENAI_API_KEY environment variable is not set')

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    try:
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": user_input}
            ],
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}}
        )
    except Exception as e:
        # 打印并记录原始异常的 repr，避免在将异常格式化到 f-string 时触发编码问题
        print("API request exception:", repr(e))
        # 抛出更安全的异常信息，同时保留原始异常作为 __cause__ 便于调试
        raise Exception("API request failed; see server logs for details") from e

    # SDK 返回的是一个 ChatCompletion 对象（含 .choices），不是 HTTP 响应，
    # 因此没有 status_code 属性。检查 choices 并返回文本。
    if hasattr(response, 'choices') and response.choices:
        try:
            content = response.choices[0].message.content
            if isinstance(content, bytes):
                try:
                    content = content.decode('utf-8')
                except Exception:
                    content = content.decode('utf-8', errors='ignore')
            return str(content)
        except Exception as e:
            print("Parse completion exception:", repr(e))
            raise Exception("无法解析完成结果") from e
    else:
        raise Exception('API 返回的 completion 中未包含 choices')

# 登出功能
@app.route('/logout')
def logout():
    session.pop('username', None)  # 从 session 中移除用户名
    return redirect(url_for('login'))

# 主页
@app.route('/')
def home():
    return redirect(url_for('register'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
