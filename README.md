# GitSight

GitSight 是一个基于 Flask 的 GitHub 项目热度排行榜示例应用。应用从本地缓存读取仓库数据，计算热度分数，并提供排行榜和项目详情页。网页访问不会直接调用 GitHub API。

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

## 刷新项目数据

手动从 GitHub API 获取项目数据并写入缓存：

```bash
python scripts/refresh_projects.py
```

默认缓存文件为 `data/projects.json`。如果缓存尚未生成，应用会回退读取 `data/repos.json` 中的示例数据。需要提高 GitHub API 访问额度时，可设置 `GITHUB_TOKEN` 环境变量。

Windows 定时任务可以使用：

```powershell
.\scripts\setup_weekly_refresh.ps1
```

## 项目结构

```text
GitSight/
├── app.py                 # 根目录启动入口
├── data/
│   ├── repos.json         # 示例仓库数据
│   └── projects.json      # GitHub API 刷新生成的本地缓存
├── src/
│   ├── __init__.py
│   ├── app.py             # Flask 应用和页面路由
│   ├── data_manager.py    # JSON 数据读写
│   ├── data_refresh.py     # 项目缓存刷新和读取
│   ├── filter.py           # Topic 筛选和个性化推荐
│   ├── github_api.py       # GitHub API 访问
│   ├── ranking.py         # 候选项目排行榜逻辑
│   └── project_detail.py  # 项目详情数据处理
├── scripts/
│   ├── build_exe.ps1             # Windows exe 打包脚本
│   ├── refresh_projects.py       # 手动刷新项目缓存
│   └── setup_weekly_refresh.ps1  # 配置 Windows 定时刷新
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

## 后续开发方向

- 增加依赖文件与部署配置
- 为热度计算和页面路由补充测试
