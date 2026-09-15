# GitSight

GitSight 是一个帮助你发现优质 GitHub 开源项目的轻量级排行榜工具。它把项目的 Stars、Forks、近期活跃度和学习适配度整理成一个直观的热度榜，让你更快找到值得关注、学习或参与的项目。

## 面向用户的产品介绍

### GitSight 能做什么

- **快速发现热门项目**：打开首页即可查看当前缓存中的 TOP10 项目和热度分数。
- **按兴趣筛选**：选择 Python、Web、机器学习等 Topic，生成更符合自己兴趣的个性化榜单。
- **了解项目详情**：点击项目可以查看中文名称、项目简介、主要语言、Stars、Forks、Issue 数量、贡献者和最近活跃情况。
- **直接访问原项目**：详情页提供 GitHub 原项目链接，方便继续阅读文档、查看代码或参与贡献。
- **适合本地使用**：Windows 用户可以直接运行 GitSight.exe；程序在本机打开网页，不需要额外安装 Python。

### 如何使用

最简单的方式是访问公开网站：

<https://sally-yixin-chen.github.io/GitSight/>

也可以下载项目发布的 Windows EXE，双击后等待浏览器自动打开。首页显示的是最近一次数据刷新生成的快照，因此打开榜单不会向 GitHub 发起请求，访问速度更稳定，也不会要求用户配置 GitHub Token。

### 榜单如何计算

GitSight 会综合项目受欢迎度、近期活跃度和学生适配度计算热度分数。分数用于帮助用户进行初步筛选，不代表项目质量的绝对结论；选择项目时仍建议结合项目文档、维护状态、Issue 和自身学习目标判断。

### 数据更新与隐私

公开网站和 EXE 使用每周一生成的项目数据快照。数据由项目维护者通过 GitHub Actions 定期刷新，普通用户不需要登录 GitHub，也不需要提供个人 Token。程序主要读取本地或公开缓存数据，不会把用户的浏览行为上传到 GitSight。

## 快速开始

```bash
git clone <仓库地址>
cd GitSight
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install Flask
python app.py
```

启动后访问 <http://127.0.0.1:5000>。

也可以直接安装项目依赖：

```bash
pip install -r requirements.txt
```

## 打包为 Windows exe

项目支持打包为 Windows 的本地 exe。打包后的程序会启动一个本地 Flask 服务，并自动打开默认浏览器；数据不会上传到其他服务器。

### 在开发电脑上打包

在项目根目录打开 PowerShell，执行：

```powershell
.\scripts\build_exe.ps1
```

打包完成后，程序位于：

```text
dist\GitSight.exe
```

EXE 使用 `static/logo.ico` 作为 Windows 图标，并将网页所需的
`static` 目录一起打包。重新打包时会使用独立的 `build-exe` 工作目录，避免旧缓存
被占用导致打包失败。

只需将 `dist\GitSight.exe` 这一个文件复制到另一台 Windows 电脑。双击后，程序会启动本地服务并打开浏览器访问 `http://127.0.0.1:5000`。

### 数据文件说明

- 打包时 `data` 目录会被内置到程序中，首次启动可以直接读取示例/缓存数据。
- 如果在源码环境执行数据刷新，重新打包即可把最新缓存带入 exe；运行中的程序也会优先读取 exe 同目录下 `data\projects.json`（该文件夹不存在时会自动创建）。
- 目标电脑不需要安装 Python；如需在目标电脑刷新 GitHub 数据，需要另行运行刷新脚本，并配置网络和 `GITHUB_TOKEN`。
- 关闭程序时，在运行窗口按 `Ctrl+C`；如果直接关闭窗口，本地服务也会停止。

### 常见问题

- **双击后浏览器没有打开**：手动访问 `http://127.0.0.1:5000`，并确认程序窗口仍在运行。
- **Windows Defender 提示未知发布者**：这是未签名的内部/个人构建程序，不代表程序一定有问题；可先确认 exe 来源。
- **换电脑后不能刷新数据**：检查目标电脑网络、GitHub 访问权限和 `GITHUB_TOKEN` 环境变量。

## 自动刷新项目数据

项目数据由 GitHub Actions 每周一北京时间 09:00 自动刷新。工作流使用
GitHub Actions 自带的 `GITHUB_TOKEN` 访问 GitHub API，不会把令牌写入 EXE。
刷新后的 `data/projects.json` 会提交回仓库，同时发布到 GitHub
Pages 的公开网站地址，供他人直接访问，也供普通用户的 EXE 下载最新数据。

首次启用时，需要在 GitHub 仓库完成以下设置：

1. 在 **Settings → Actions → General** 中，将 Workflow permissions 设为
   **Read and write permissions**。
2. 在 **Settings → Pages** 中，将 Source 设为 **GitHub Actions**。
3. 在 **Actions → Refresh and publish project data** 中手动运行一次。
4. 确认以下地址可以在未登录 GitHub 的浏览器中打开：
   `https://sally-yixin-chen.github.io/GitSight/`

如果当前 GitHub 账号/组织不允许使用 GitHub Pages，需要把工作流中的
`_site` 目录改为发布到其他公开静态托管服务，并将 `GITSIGHT_PUBLIC_DATA_URL`
改成新的 `projects.json` 地址。EXE 中不放置 GitHub Token。

`app.py`、`GitSight.exe` 和 GitHub Pages 公网网址都只读取本周一生成的缓存快照，
打开应用或访问网页不会调用 GitHub API。EXE 打包时会把 `data/projects.json` 内置
到程序中，因此每次启动都使用该周快照；需要更新数据时，由周一的 GitHub Actions
重新生成缓存并重新打包 EXE。

开发者仍可以手动从 GitHub API 获取项目数据并写入本地缓存：

```bash
python scripts/refresh_projects.py
```

默认缓存文件为 `data/projects.json`。如果缓存尚未生成，应用会回退读取 `data/repos.json` 中的示例数据。
只有 `scripts/refresh_projects.py` 和 GitHub Actions 的周一任务会调用 GitHub API；需要提高
GitHub API 访问额度时，可设置 `GITHUB_TOKEN` 环境变量。

## 维护项目中文名和中文介绍

项目列表中的中文信息维护在 `data/project_locales.json`。对象的键必须使用 GitHub
仓库的完整名称，例如 `facebook/react`；`name` 是中文项目名，`description` 是列表
中显示的中文介绍。每周一刷新时，已有人工中文简介优先；GitHub 返回的简介如果本身
是中文则直接保存，否则使用百度通用文本翻译 API 补充缺失翻译。需要在仓库 Actions
Secrets 中配置 `BAIDU_APP_ID` 和 `BAIDU_SECRET_KEY`；没有密钥或翻译失败时，页面
回退到英文简介或默认提示。程序将每月翻译字符安全上限设为 90 万，避免超过免费额度。

开发者也可以使用 Windows 定时任务：

```powershell
.\scripts\setup_weekly_refresh.ps1
```

## 项目结构

```text
GitSight/
├── .github/
│   └── workflows/
│       └── refresh-and-publish.yml  # 每周刷新并发布公开数据
├── app.py                 # 根目录启动入口
├── data/
│   ├── repos.json         # 示例仓库数据
│   ├── project_locales.json # 项目中文名和中文介绍
│   └── projects.json      # GitHub API 刷新生成的本地缓存
├── src/
│   ├── __init__.py
│   ├── app.py             # Flask 应用和页面路由
│   ├── data_manager.py    # JSON 数据读写
│   ├── data_refresh.py     # 项目缓存刷新和读取
│   ├── remote_data.py      # 下载公开项目缓存并保存到本地
│   ├── filter.py           # Topic 筛选和个性化推荐
│   ├── github_api.py       # GitHub API 访问
│   ├── ranking.py         # 候选项目排行榜逻辑
│   └── project_detail.py  # 项目详情数据处理
├── scripts/
│   ├── build_exe.ps1             # Windows exe 打包脚本
│   ├── refresh_projects.py       # 手动刷新项目缓存
│   └── setup_weekly_refresh.ps1  # 配置 Windows 定时刷新
├── static/
│   └── logo.ico                  # 应用和网页使用的图标
├── requirements.txt               # Python 运行与打包依赖
├── GitSight.spec                  # PyInstaller 打包配置
└── README.md
```

应用代码统一放在 `src/`，数据文件统一放在 `data/`，运维脚本统一放在 `scripts/`，根目录的 `app.py` 仅作为启动入口。

## GitHub 协作约定

1. 从 `main` 创建功能分支，例如 `feature/project-detail`。
2. 每次提交只完成一个清晰的功能或修复，并写明提交信息。
3. 推送分支后创建 Pull Request，至少由一名成员 review 后再合并。
4. 合并前确认应用可以正常启动，并同步最新的 `main` 分支。

## 维护建议

如果继续扩展项目，建议为热度计算、筛选逻辑和页面路由补充自动化测试，并在发布前验证
Windows EXE 和 GitHub Pages 页面均能正常启动与访问。
