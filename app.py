"""GitPulse 启动入口。"""

from src.app import app


if __name__ == "__main__":
    app.run(debug=True)
