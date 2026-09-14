$ErrorActionPreference = "Stop"

Write-Host "正在安装/检查打包依赖..."
python -m pip install -r requirements.txt

Write-Host "正在清理本次打包目录..."
if (Test-Path build) { Remove-Item -LiteralPath build -Recurse -Force }
if (Test-Path dist) { Remove-Item -LiteralPath dist -Recurse -Force }

Write-Host "正在生成 dist\GitSight.exe..."
python -m PyInstaller --noconfirm --clean GitSight.spec

Write-Host "打包完成：dist\GitSight.exe"
Write-Host "只需将这个 exe 文件复制到目标电脑。"
