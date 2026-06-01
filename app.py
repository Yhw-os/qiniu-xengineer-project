from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, Flask!"

if __name__ == "__main__":
    import webbrowser
    import threading
    import os

    def _open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/")

    # When using the reloader, the process runs twice. Only open browser
    # in the child process (WERKZEUG_RUN_MAIN == "true").
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, _open_browser).start()

    app.run(debug=True)



