"""GitSight Flask 应用入口。"""

from typing import Any, Dict, List

from flask import Flask, abort, render_template_string, request, url_for

try:
    from .data_refresh import get_diverse_topics, load_cached_projects
    from .filter import get_personalized_top_projects
    from .project_detail import get_project_by_name, get_project_detail
    from .ranking import rank_projects
except ImportError:
    # 兼容直接执行 ``python src/app.py`` 的场景。
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from src.data_refresh import get_diverse_topics, load_cached_projects
    from src.filter import get_personalized_top_projects
    from src.project_detail import get_project_by_name, get_project_detail
    from src.ranking import rank_projects

app = Flask(__name__)


def load_projects() -> List[Dict[str, Any]]:
    """只读取本地缓存；访客访问网站不会调用 GitHub API。"""
    return load_cached_projects()


def ranked_projects(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """计算并返回带热度分数的项目列表。"""
    return rank_projects(projects)


PAGE_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');
:root { --bg:#f8fafc; --surface:#ffffff; --surface-2:#f1f5f9; --border:#e2e8f0; --text:#1e293b; --muted:#475569; --accent:#2563eb; --accent-dark:#eff6ff; --link:#2563eb; --radius:18px; }
* { box-sizing:border-box; }
body { margin:0; min-width:320px; background:radial-gradient(circle at top right, #dbeafe 0, transparent 34%), var(--bg); color:var(--text); font-family:'IBM Plex Sans',system-ui,sans-serif; line-height:1.5; }
a { color:var(--link); text-decoration:none; } a:hover { text-decoration:underline; }
.shell { width:min(1180px, calc(100% - 32px)); margin:0 auto; padding:28px 0 56px; }
.topbar { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:36px; }
.brand { display:flex; align-items:center; gap:10px; color:var(--text); font-family:'JetBrains Mono',monospace; font-weight:600; letter-spacing:-.04em; }
.brand-mark { display:grid; place-items:center; width:34px; height:34px; border:1px solid #93c5fd; border-radius:10px; color:var(--accent); background:#eff6ff; } .brand-mark svg { width:20px; height:20px; fill:none; stroke:currentColor; stroke-width:2; }
.status { display:flex; align-items:center; gap:8px; color:var(--muted); font-size:.875rem; }
.status-dot { width:8px; height:8px; background:var(--accent); border-radius:50%; box-shadow:0 0 0 4px rgba(37,99,235,.12); }
.hero { display:grid; grid-template-columns:1.45fr .9fr; gap:24px; align-items:end; margin-bottom:24px; }
.eyebrow { margin:0 0 9px; color:var(--accent); font:600 .78rem 'JetBrains Mono',monospace; letter-spacing:.1em; text-transform:uppercase; }
h1 { margin:0; max-width:720px; font-size:clamp(1.8rem,3.35vw,3.05rem); line-height:1.12; letter-spacing:-.04em; }
.title-accent { color:#1d4ed8; background:linear-gradient(transparent 67%,#dbeafe 67%); padding:0 .05em; }
.hero-copy { max-width:58ch; margin:16px 0 0; color:var(--muted); font-size:1.05rem; }
.metric-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; }
.metric { min-height:102px; padding:17px; background:linear-gradient(145deg,#ffffff,#f8fbff); border:1px solid var(--border); border-radius:var(--radius); }
.metric-label { display:block; color:var(--muted); font-size:.78rem; } .metric-value { display:block; margin-top:6px; font:600 1.6rem 'JetBrains Mono',monospace; color:#0f172a; }
.panel { padding:22px; background:rgba(255,255,255,.94); border:1px solid var(--border); border-radius:var(--radius); box-shadow:0 18px 42px rgba(15,23,42,.07); }
.panel-head { display:flex; align-items:flex-start; justify-content:space-between; gap:18px; margin-bottom:17px; } .panel h2 { margin:0; font-size:1.05rem; letter-spacing:-.02em; } .panel-note { margin:3px 0 0; color:var(--muted); font-size:.9rem; }
.filters { display:flex; align-items:center; flex-wrap:wrap; gap:10px; padding:0; border:0; margin:0; }
.filters legend { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
.topic { position:relative; display:inline-flex; } .topic input { position:absolute; opacity:0; inset:0; cursor:pointer; }
.topic span { display:flex; align-items:center; min-height:44px; padding:8px 12px; border:1px solid var(--border); border-radius:999px; color:#334155; font:.82rem 'JetBrains Mono',monospace; transition:background .18s ease,border-color .18s ease,color .18s ease; }
.topic input:checked + span { background:var(--accent-dark); border-color:var(--accent); color:#1d4ed8; } .topic input:focus-visible + span, button:focus-visible, .clear:focus-visible, .project-link:focus-visible { outline:3px solid #1d4ed8; outline-offset:3px; }
button { min-height:44px; padding:9px 15px; border:1px solid var(--accent); border-radius:10px; background:var(--accent); color:#fff; font-weight:700; cursor:pointer; transition:transform .18s ease,background .18s ease; } button:hover { transform:translateY(-1px); background:#1d4ed8; } .clear { display:inline-flex; align-items:center; min-height:44px; padding:9px 2px; color:var(--muted); font-size:.9rem; }
.table-wrap { overflow-x:auto; margin-top:18px; border:1px solid var(--border); border-radius:14px; } table { width:100%; min-width:660px; border-collapse:collapse; } th { padding:12px 16px; color:var(--muted); background:#f8fafc; font:600 .72rem 'JetBrains Mono',monospace; letter-spacing:.08em; text-align:left; text-transform:uppercase; } td { padding:16px; border-top:1px solid var(--border); } tbody tr { transition:background .18s ease; } tbody tr:hover { background:#f8fbff; }
.rank { color:#2563eb; font:600 .82rem 'JetBrains Mono',monospace; } .project-link { color:var(--text); font-weight:600; } .project-link:hover { color:#2563eb; text-decoration:none; } .score { color:#1d4ed8; font:600 .9rem 'JetBrains Mono',monospace; } .mono { font-family:'JetBrains Mono',monospace; font-size:.88rem; }
.back { display:inline-flex; align-items:center; margin-bottom:28px; color:var(--muted); } .back:hover { color:#2563eb; text-decoration:none; }
.detail-hero { padding:34px; margin-bottom:20px; background:linear-gradient(135deg,#eff6ff,#ffffff 58%,#f0fdf4); border:1px solid #bfdbfe; border-radius:22px; } .detail-hero h1 { font-size:clamp(2rem,5vw,3.6rem); } .detail-description { max-width:720px; color:#334155; font-size:1.06rem; }
.cards { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:20px; } .card { padding:20px; background:var(--surface); border:1px solid var(--border); border-radius:14px; color:var(--muted); } .card .score { display:block; margin-top:8px; font-size:1.85rem; color:#0f172a; }
.detail-table td:first-child { width:35%; color:var(--muted); } .external-link { display:inline-flex; align-items:center; min-height:44px; margin-top:20px; padding:10px 14px; border:1px solid #bfdbfe; border-radius:10px; color:#1d4ed8; }
@media (max-width:760px) { .shell { width:min(100% - 24px,1180px); padding-top:18px; } .topbar { margin-bottom:28px; } .hero { grid-template-columns:1fr; } h1 { font-size:2rem; } .metric-grid { max-width:430px; } .panel { padding:16px; } .panel-head { display:block; } .filters { margin-top:14px; } .cards { grid-template-columns:1fr; } .detail-hero { padding:24px; } }
@media (prefers-reduced-motion:reduce) { *,*::before,*::after { scroll-behavior:auto!important; transition:none!important; animation:none!important; } }
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
        """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>GitSight 热度排行榜</title>"""
        + PAGE_STYLE
        + """</head><body><main class='shell'>
        <header class='topbar'><a class='brand' href='{{ url_for("index") }}'><span class='brand-mark' aria-hidden='true'><svg viewBox='0 0 24 24'><path d='M4 16.5 9 11l3 3 8-8'/><path d='M15 6h5v5'/></svg></span>GitSight</a><span class='status'><span class='status-dot' aria-hidden='true'></span>缓存数据已就绪</span></header>
        <section class='hero'><div><p class='eyebrow'>See GitHub. See What's Next.</p><h1>GitHub 热门项目<br><span class='title-accent'>排行榜</span></h1><p class='hero-copy'>GitHub风向，洞见未来<br>选择兴趣标签，查看你的专属 TOP10</p></div>
        <div class='metric-grid'><div class='metric'><span class='metric-label'>缓存项目</span><strong class='metric-value'>{{ project_count }}</strong></div><div class='metric'><span class='metric-label'>当前榜单</span><strong class='metric-value'>TOP {{ projects|length }}</strong></div></div></section>
        <section class='panel'><div class='panel-head'><div><h2>按兴趣定制榜单</h2><p class='panel-note'>从 15 个差异化 GitHub Topic 中选择，立即得到个性化热度排行。</p></div><a class='clear' href='{{ url_for("index") }}'>重置筛选</a></div>
        <form method='get'><fieldset class='filters'><legend>选择感兴趣的项目标签</legend>{% for topic in topics %}<label class='topic'><input type='checkbox' name='topic' value='{{ topic }}' {% if topic in selected_topics %}checked{% endif %}><span>{{ topic }}</span></label>{% endfor %}<button type='submit'>生成 TOP10</button></fieldset></form>
        <div class='table-wrap'><table><thead><tr><th>排名</th><th>项目</th><th>热度分数</th><th>Stars</th><th>Forks</th></tr></thead><tbody>
        {% for project in projects %}<tr><td class='rank'>#{{ '%02d'|format(loop.index) }}</td><td><a class='project-link' href='{{ url_for("project_detail", name=project.full_name or project.name) }}'>{{ project.full_name or project.name }}</a></td>
        <td class='score'>{{ project.hot_score }}</td><td class='mono'>{{ project.stars }}</td><td class='mono'>{{ project.forks }}</td></tr>{% endfor %}
        </tbody></table></div></section></main></body></html>""",
        projects=ranked,
        topics=get_diverse_topics(projects, limit=15),
        selected_topics=selected_topics,
        project_count=len(projects),
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
        """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>{{ detail.name }}</title>"""
        + PAGE_STYLE
        + """</head><body><main class='shell'><a class='back' href='{{ url_for("index") }}'>← 返回热门榜单</a>
        <section class='detail-hero'><p class='eyebrow'>项目详情</p><h1>{{ detail.name }}</h1><p class='detail-description'>{{ detail.description }}</p></section>
        <div class='cards'><div class='card'>热度分数<strong class='score'>{{ detail.hot_score }}</strong></div>
        <div class='card'>Stars<strong class='score'>{{ detail.stars }}</strong></div><div class='card'>Forks<strong class='score'>{{ detail.forks }}</strong></div></div>
        <section class='panel'><div class='panel-head'><div><h2>项目数据</h2><p class='panel-note'>最近一次缓存同步时记录的信息。</p></div></div><div class='table-wrap'><table class='detail-table'><tbody>
        <tr><td>项目所有者</td><td>{{ detail.owner }}</td></tr><tr><td>主要语言</td><td>{{ detail.language }}</td></tr>
        <tr><td>开放 Issue</td><td>{{ detail.open_issues }}</td></tr><tr><td>贡献者</td><td>{{ detail.contributors }}</td></tr>
        <tr><td>最近更新（天前）</td><td>{{ detail.last_push_days }}</td></tr><tr><td>项目大小（KB）</td><td>{{ detail.size_kb }}</td></tr>
        </tbody></table></div><a class='external-link' href='{{ detail.url }}' target='_blank' rel='noopener'>在 GitHub 查看原项目</a></section></main></body></html>""",
        detail=detail,
    )
if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
