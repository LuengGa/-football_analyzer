#!/bin/bash
# Git 仓库清理脚本
# 用于彻底清理 .git 目录中的历史大文件

set -e

echo "=========================================="
echo "Git 仓库彻底清理脚本"
echo "=========================================="
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# 检查是否在 git 仓库中
if [ ! -d ".git" ]; then
    echo "❌ 当前目录不是 Git 仓库"
    exit 1
fi

echo "📊 当前 .git 目录大小:"
du -sh .git
echo ""

# 确认操作
echo "⚠️  警告：此操作将删除 .git 目录并重新初始化"
echo "   所有 Git 历史记录将被永久删除！"
echo ""
read -p "是否继续？(y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "操作已取消"
    exit 0
fi

echo ""
echo "🔄 正在执行清理..."
echo ""

# 1. 删除 .git 目录
echo "1️⃣ 删除 .git 目录..."
rm -rf .git
echo "   ✅ 已删除"

# 2. 重新初始化 git（可选）
echo ""
read -p "是否重新初始化 Git 仓库？(y/N): " reinit

if [ "$reinit" = "y" ] || [ "$reinit" = "Y" ]; then
    echo ""
    echo "2️⃣ 重新初始化 Git 仓库..."
    git init

    # 创建 .gitignore（如果不存在）
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/

# Data files (large)
*.json
*.db
*.sqlite
*.sqlite3
data/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
EOF
        echo "   ✅ 已创建 .gitignore"
    fi

    echo ""
    echo "3️⃣ 初始提交..."
    git add -A
    git commit -m "Initial commit (cleaned)"
    echo "   ✅ 已创建初始提交"
fi

echo ""
echo "=========================================="
echo "✅ 清理完成！"
echo "=========================================="
echo ""
echo "📊 清理后项目大小:"
du -sh .
echo ""
echo "📝 .gitignore 已配置，自动忽略:"
echo "   - 大数据文件 (*.json, *.db, data/)"
echo "   - Python 缓存 (__pycache__/)"
echo "   - IDE 配置 (.vscode/, .idea/)"
echo "   - 虚拟环境 (venv/, env/)"
echo ""
