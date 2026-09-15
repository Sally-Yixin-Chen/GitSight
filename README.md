# GitSight

🎓 GitSight，专为信息类大学生打造的 GitHub 热门项目发现工具！
🌍 From GitHub, See a Bigger World.
💻 GitSight 致力于帮助更多信息类大学生无门槛接触 GitHub、探索开源社区。无论是闲暇时打发时间，还是想寻找课程学习、项目实践的灵感，都可以通过中文友好的项目名称与简介，快速了解值得关注的开源项目。
🔍 页面简洁直观，支持按 Python、ai等兴趣标签筛选，每周一9：00定时刷新。从热门榜单到项目详情，从 Stars、Forks 到近期活跃度，点击下方网址即可开启你的开源之旅！
🔗 [点击访问 GitSight 在线网站](https://sally-yixin-chen.github.io/GitSight/)

## 一、适合谁使用

- **零基础用户**：无需登录 GitHub 或配置 Token，直接浏览中文榜单和项目简介。
- **学习者**：按兴趣标签查找适合课程学习、练习和项目实践的开源项目。
- **开发者**：查看项目热度和活跃度，并通过详情页进入 GitHub 原项目继续阅读代码或参与贡献。

榜单分数用于辅助筛选，不代表项目质量的绝对结论。选择项目时仍建议结合项目文档、维护状态、Issue 和自己的学习目标进行判断。

## 二、快速开始

### 1. 直接使用

访问在线网站即可：

<https://sally-yixin-chen.github.io/GitSight/>

### 2. 本地运行

需要 Python 3.13 或兼容版本：

```bash
git clone <仓库地址>
cd GitSight
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux：source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

启动后访问 <http://127.0.0.1:5000>。应用默认读取本地缓存，不会因打开页面而请求 GitHub API。

### 3. Windows EXE

在项目根目录运行：

```powershell
.\scripts\build_exe.ps1
```

生成的文件位于 `dist\GitSight.exe`。将 EXE 复制到 Windows 电脑后双击即可启动本地服务并打开浏览器，目标电脑无需安装 Python。EXE 使用打包时内置的数据快照；要获得最新数据，需要重新刷新数据并打包。

## 三、工作原理

GitSight 将“数据获取”和“页面访问”分开：

1. `scripts/refresh_projects.py` 调用 GitHub API，获取候选项目并写入 `data/projects.json`。
2. `src/ranking.py` 根据 Stars、Forks、近期活跃度等指标计算热度排序。
3. `src/filter.py` 按 GitHub Topic 筛选项目，生成兴趣榜单。
4. `src/project_detail.py` 整理详情页字段；`data/project_locales.json` 提供中文名称和简介。
5. Flask 应用读取缓存并提供网页，`scripts/build_static_site.py` 生成可部署到 GitHub Pages 的静态网站。

这种设计让普通用户访问网站时不需要 GitHub Token，也不会受到 GitHub API 实时限流影响。

## 四、数据更新与发布

GitHub Actions 工作流 `.github/workflows/refresh-and-publish.yml` 每周一北京时间 09:00 自动执行，也支持手动运行。它会刷新项目缓存、翻译缺失的中文简介、将更新后的数据提交回仓库，并构建部署 GitHub Pages 网站。

如需手动刷新本地数据：

```bash
python scripts/refresh_projects.py
```

默认数据文件为 `data/projects.json`。如果该文件不存在，应用会回退读取 `data/repos.json` 中的示例数据。需要提高 GitHub API 访问额度时，可设置 `GITHUB_TOKEN` 环境变量。

中文名称和简介维护在 `data/project_locales.json`，键名使用 GitHub 仓库完整名称，例如 `facebook/react`。缺少翻译密钥或翻译失败时，程序会回退到英文简介或默认提示。

## 五、项目结构

```text
GitSight/
├── app.py                         # 本地启动入口
├── src/
│   ├── app.py                     # Flask 应用和路由
│   ├── data_manager.py            # JSON 数据读写
│   ├── data_refresh.py            # 缓存刷新和读取
│   ├── remote_data.py             # 下载公开缓存
│   ├── github_api.py              # GitHub API 访问
│   ├── ranking.py                 # 热度排序
│   ├── filter.py                  # Topic 筛选
│   └── project_detail.py          # 项目详情处理
├── data/
│   ├── repos.json                 # 示例数据
│   ├── projects.json              # 刷新生成的项目缓存
│   └── project_locales.json       # 中文名称和简介
├── scripts/
│   ├── refresh_projects.py        # 手动刷新数据
│   ├── translate_locales.py       # 翻译中文简介
│   ├── build_static_site.py       # 构建静态网站
│   └── build_exe.ps1              # 打包 Windows EXE
├── .github/workflows/
│   └── refresh-and-publish.yml    # 定时刷新与发布
├── requirements.txt
└── GitSight.spec                  # PyInstaller 配置
```

应用代码、数据文件和运维脚本分别集中在 `src/`、`data/` 和 `scripts/`，便于定位和维护。

## 六、GitHub Actions 配置

首次启用自动发布时，请在仓库中确认：

1. **Settings → Actions → General → Workflow permissions** 设置为允许读写。
2. **Settings → Pages → Source** 选择 **GitHub Actions**。
3. 在 **Actions** 中手动运行一次 **Refresh and publish project data**。
4. 检查在线地址是否可以正常访问。

## 七、开发提示

提交功能或修复前，建议先确认本地 Flask 应用可以启动，并检查榜单筛选、项目详情和数据刷新流程。项目当前以缓存快照为核心，修改数据结构时需要同时关注本地应用、静态网站和 EXE 三种使用方式。
