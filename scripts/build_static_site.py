"""Render the current GitSight ranking as a static GitHub Pages site."""

from __future__ import annotations

import shutil
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app import app, load_projects
from src.data_refresh import get_diverse_topics
from src.ranking import rank_projects
from src.runtime_paths import BUNDLED_LEGACY_DATA_FILE, DEFAULT_DATA_FILE


SITE_ROOT = PROJECT_ROOT / "_site"


def _static_path(html: bytes, nested: bool = False) -> bytes:
    """Rewrite Flask absolute URLs for GitHub Pages static hosting."""
    text = html.decode("utf-8")
    prefix = "../../../" if nested else ""
    text = text.replace('href="/"', f'href="{prefix}./"')
    text = text.replace("href='/'", f"href='{prefix}./'")
    text = text.replace('src="/static/', f'src="{prefix}static/')
    text = text.replace("src='/static/", f"src='{prefix}static/")
    text = text.replace('href="/static/', f'href="{prefix}static/')
    text = text.replace("href='/static/", f"href='{prefix}static/")
    return text.encode("utf-8")


def _detail_relative_path(full_name: str) -> Path:
    owner, _, repository = full_name.partition("/")
    return SITE_ROOT / "project" / owner / repository / "index.html"


def _add_static_filter(html: bytes, ranked: list[dict[str, object]]) -> bytes:
    """Add client-side topic filtering so the static homepage remains interactive."""
    payload = json.dumps(ranked, ensure_ascii=False).replace("<", "\\u003c")
    html = html.replace(
        "<button type='submit'>生成 TOP10</button>".encode("utf-8"),
        "<button type='button' id='gitsight-filter-submit'>生成 TOP10</button>".encode("utf-8"),
    )
    script = f"""
<script type="application/json" id="gitsight-data">{payload}</script>
<script>
(() => {{
  const data = JSON.parse(document.getElementById('gitsight-data').textContent);
  const form = document.querySelector('form');
  const tbody = document.querySelector('tbody');
  const clear = document.querySelector('.clear');
  const submit = document.querySelector('#gitsight-filter-submit');
  const count = document.querySelector('.metric-grid .metric:last-child .metric-value');
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
  const detailUrl = (p) => {{
    const parts = String(p.full_name || p.name || '').split('/');
    return `project/${{encodeURIComponent(parts[0])}}/${{encodeURIComponent(parts[1] || parts[0])}}/`;
  }};
  const ownerLabel = (p) => {{
    const parts = String(p.full_name || p.name || '').split('/');
    return `${{esc(parts[1] || parts[0])}} —— ${{esc(p.owner || parts[0] || '')}}`;
  }};
  const render = (selected) => {{
    const interests = new Set(selected.map((x) => x.toLowerCase()));
    const visible = data.filter((p) => !interests.size || (p.topics || []).some((t) => interests.has(String(t).toLowerCase()))).slice(0, 10);
    tbody.innerHTML = visible.map((p, i) => {{
      const medal = i === 0 ? '<span class="medal medal-gold" aria-label="第1名">🥇</span>' : i === 1 ? '<span class="medal medal-silver" aria-label="第2名">🥈</span>' : i === 2 ? '<span class="medal medal-bronze" aria-label="第3名">🥉</span>' : '';
      return `<tr><td class="rank">${{medal}}<span class="rank-number">${{String(i + 1).padStart(2, '0')}}</span></td><td><a class="project-link" href="${{detailUrl(p)}}"><span class="project-name">${{esc(p.chinese_name || p.name)}}</span><span class="project-repository">${{ownerLabel(p)}}</span></a><p class="project-description">${{esc(p.chinese_description || '')}}</p></td><td class="score">${{esc(p.hot_score)}}</td><td class="mono">${{esc(p.stars)}}</td><td class="mono">${{esc(p.forks)}}</td></tr>`;
    }}).join('');
    count.textContent = `TOP ${{visible.length}}`;
  }};
  submit.addEventListener('click', () => render([...form.querySelectorAll('input[name="topic"]:checked')].map((x) => x.value)));
  clear.addEventListener('click', (event) => {{ event.preventDefault(); form.reset(); render([]); }});
  render([]);
}})();
</script>
"""
    return html.replace(b"</body>", script.encode("utf-8") + b"</body>")


def main() -> int:
    SITE_ROOT.mkdir(parents=True, exist_ok=True)
    projects = load_projects()
    ranked = rank_projects(projects)
    response = app.test_client().get("/")
    if response.status_code != 200:
        raise RuntimeError(f"首页渲染失败：HTTP {response.status_code}")
    (SITE_ROOT / "index.html").write_bytes(_add_static_filter(_static_path(response.data), ranked))

    client = app.test_client()
    for project in projects:
        full_name = str(project.get("full_name") or project.get("name") or "").strip()
        if "/" not in full_name:
            continue
        detail_response = client.get(f"/project/{full_name}")
        if detail_response.status_code != 200:
            raise RuntimeError(f"详情页渲染失败：{full_name} HTTP {detail_response.status_code}")
        detail_path = _detail_relative_path(full_name)
        detail_path.parent.mkdir(parents=True, exist_ok=True)
        detail_path.write_bytes(_static_path(detail_response.data, nested=True))

    data_source = DEFAULT_DATA_FILE if DEFAULT_DATA_FILE.exists() else BUNDLED_LEGACY_DATA_FILE
    if data_source.exists():
        shutil.copy2(data_source, SITE_ROOT / "projects.json")

    static_source = PROJECT_ROOT / "static"
    static_target = SITE_ROOT / "static"
    if static_target.exists():
        shutil.rmtree(static_target)
    shutil.copytree(static_source, static_target)
    (SITE_ROOT / "health.json").write_text('{"status":"ok"}\n', encoding="utf-8")
    print(f"Static site written to {SITE_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
