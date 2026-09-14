"""GitPulse Flask 应用入口。"""

from typing import Any, Dict, List

from flask import Flask, abort, render_template_string, request, url_for

from .data_refresh import get_available_topics, load_cached_projects
from .filter import get_personalized_top_projects
from .project_detail import get_project_by_name, get_project_detail
from .ranking import rank_projects

app = Flask(__name__)


def load_projects() -> List[Dict[str, Any]]:
    """只读取本地缓存；访客访问网站不会调用 GitHub API。"""
    return load_cached_projects()


def ranked_projects(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """计算并返回带热度分数的项目列表。"""
    return rank_projects(projects)


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
    """显示缓存项目的热门榜或按 Topic 筛选后的个性化 TOP10。"""
    projects = load_projects()
    if not projects:
        abort(503, description="尚未生成项目缓存，请等待每周定时刷新完成。")

    selected_topics = request.args.getlist("topic")
    ranked = get_personalized_top_projects(projects, selected_topics, limit=10)
    return render_template_string(
        """<!doctype html><html><head><meta charset='utf-8'><title>GitPulse 热度排行榜</title>"""
        + PAGE_STYLE
        + """</head><body><h1>GitPulse 项目热度排行榜</h1>
        <p>数据由后台每周更新；浏览网站不会调用 GitHub API。</p>
        <form class='toolbar' method='get'>
        {% for topic in topics %}<label><input type='checkbox' name='topic' value='{{ topic }}'
        {% if topic in selected_topics %}checked{% endif %}> {{ topic }}</label>{% endfor %}
        <button type='submit'>生成个性化 TOP10</button><a href='{{ url_for("index") }}'>清除筛选</a></form>
        <table><tr><th>排名</th><th>项目</th><th>热度分数</th><th>Stars</th><th>Forks</th></tr>
        {% for project in projects %}<tr><td>{{ loop.index }}</td>
        <td><a href='{{ url_for("project_detail", name=project.full_name or project.name) }}'>{{ project.full_name or project.name }}</a></td>
        <td>{{ project.hot_score }}</td><td>{{ project.stars }}</td><td>{{ project.forks }}</td></tr>{% endfor %}
        </table></body></html>""",
        projects=ranked,
        topics=get_available_topics(projects),
        selected_topics=selected_topics,
    )


@app.route("/project/<path:name>")
def project_detail(name: str):
    """从缓存读取项目详情，不向 GitHub 发起请求。"""
    projects = load_projects()
    if not projects:
        abort(503, description="尚未生成项目缓存，请等待每周定时刷新完成。")
    project = get_project_by_name(ranked_projects(projects), name)
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
if __name__ == "__main__":
    app.run(debug=True)
