# GitPulse

GitPulse 是一个基于 Flask 的 GitHub 项目热度排行榜示例应用。项目从 `repos.json` 读取仓库数据，计算热度分数，并提供排行榜和项目详情页。

## 快速开始

```bash
git clone <仓库地址>
cd GitPulse
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install Flask
python app.py
```

启动后访问 <http://127.0.0.1:5000>。

## 项目结构

```text
GitPulse/
├── app.py                 # 根目录启动入口
├── data/
│   └── repos.json         # 示例仓库数据
├── src/
│   ├── __init__.py
│   ├── app.py             # Flask 应用和页面路由
│   ├── hotrank.py         # 多维度热度分数计算
│   ├── ranking.py         # 候选项目排行榜逻辑
│   └── project_detail.py  # 项目详情数据处理
└── README.md
```

应用代码统一放在 `src/gitpulse/`，数据文件统一放在 `data/`，根目录的 `app.py` 仅作为启动入口。

## GitHub 协作约定

1. 从 `main` 创建功能分支，例如 `feature/project-detail`。
2. 每次提交只完成一个清晰的功能或修复，并写明提交信息。
3. 推送分支后创建 Pull Request，至少由一名成员 review 后再合并。
4. 合并前确认应用可以正常启动，并同步最新的 `main` 分支。

## 后续开发方向

- 接入 GitHub API，自动刷新仓库数据
- 为热度计算和页面路由补充测试
- 增加依赖文件与部署配置
