"""GitPulse Flask 应用入口。"""

import json
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, abort, redirect, render_template_string, request, url_for

from .hotrank import compute_hotrank
from .project_detail import get_project_by_name, get_project_detail


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "repos.json"

app = Flask(__name__)


def load_projects() -> List[Dict[str, Any]]:
    """从 JSON 文件读取项目数据。"""
    with DATA_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def ranked_projects(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """计算并返回带热度分数的项目列表。"""
    ranked, _ = compute_hotrank(projects)
    return ranked


PAGE_STYLE = """
<style>
body { font-family: Arial, sans-serif; max-width: 960px; margin: 40px auto; padding: 0 20px; color: #243447; }
h1 { color: #172b4d; } a { color: #1769aa; text-decoration: none; }
.toolbar { display: flex; gap: 12px; margin: 20px 0; }
button, input { padding: 8px 12px; border: 1px solid #ccd6e0; border-radius: 6px; }
button { background: #1769aa; color: white; cursor: pointer; }
table { width: 100%; border-collapse: collapse; } th, td { padding: 12px; border-bottom: 1px solid #e6ebf0; text-align: left; }
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.card { padding: 16px; background: #f5f8fb; border-radius: 8px; } .score { font-size: 28px; font-weight: bold; color: #1769aa; }
</style>
"""


@app.route("/")
def index():
    """Flask 首页，显示项目热度排行榜。"""
    projects = ranked_projects(load_projects())
    return render_template_string(
        """<!doctype html><html><head><meta charset='utf-8'><title>GitPulse 热度排行榜</title>"""
        + PAGE_STYLE
        + """</head><body><h1>GitPulse 项目热度排行榜</h1>
        <div class='toolbar'><form action='{{ url_for("refresh_data") }}' method='post'><button>刷新数据</button></form></div>
        <table><tr><th>排名</th><th>项目</th><th>热度分数</th><th>Stars</th><th>Forks</th></tr>
        {% for project in projects %}<tr><td>{{ loop.index }}</td>
        <td><a href='{{ url_for("project_detail", name=project.name) }}'>{{ project.name }}</a></td>
        <td>{{ project.hot_score }}</td><td>{{ project.stars }}</td><td>{{ project.forks }}</td></tr>{% endfor %}
        </table></body></html>""",
        projects=projects,
    )


@app.route("/project/<path:name>")
def project_detail(name: str):
    """项目详情页。"""
    projects = ranked_projects(load_projects())
    project = get_project_by_name(projects, name)
    detail = get_project_detail(project)
    if detail is None:
        abort(404, description="找不到这个项目")

    return render_template_string(
        """<!doctype html><html><head><meta charset='utf-8'><title>{{ detail.name }}</title>"""
        + PAGE_STYLE
        + """</head><body><p><a href='{{ url_for("index") }}'>← 返回排行榜</a></p>
        <h1>{{ detail.name }}</h1><p>{{ detail.description }}</p>
        <div class='cards'><div class='card'>热度分数<div class='score'>{{ detail.hot_score }}</div></div>
        <div class='card'>Stars<div class='score'>{{ detail.stars }}</div></div>
        <div class='card'>Forks<div class='score'>{{ detail.forks }}</div></div></div>
        <h2>项目数据</h2><table>
        <tr><th>项目所有者</th><td>{{ detail.owner }}</td></tr><tr><th>主要语言</th><td>{{ detail.language }}</td></tr>
        <tr><th>开放 Issue</th><td>{{ detail.open_issues }}</td></tr><tr><th>贡献者</th><td>{{ detail.contributors }}</td></tr>
        <tr><th>最近更新（天前）</th><td>{{ detail.last_push_days }}</td></tr><tr><th>项目大小（KB）</th><td>{{ detail.size_kb }}</td></tr>
        </table><p><a href='{{ detail.url }}' target='_blank'>在 GitHub 查看原项目</a></p>
        </body></html>""",
        detail=detail,
    )


@app.route("/refresh", methods=["POST"])
def refresh_data():
    """可选的数据刷新入口；当前返回首页，便于以后接入 GitHub API。"""
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
