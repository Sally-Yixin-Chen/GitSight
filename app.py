"""GitSight 启动入口。"""

import threading
import webbrowser

from src.app import app


def open_browser() -> None:
    """服务启动后打开默认浏览器。"""
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=False, host="127.0.0.1", port=5000)
