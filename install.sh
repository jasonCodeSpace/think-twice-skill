#!/bin/bash
# Think-Twice 安装脚本

set -e

echo "🚀 Think-Twice 安装向导"
echo "======================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境并安装依赖
echo ""
echo "📦 安装依赖..."
source venv/bin/activate
pip install -q -r requirements.txt
echo "✅ 依赖安装完成"

# 创建数据目录
mkdir -p data

# 检查数据文件
if [ ! -f "data/startups_classified.json" ] || [ ! -f "data/startups_vectors.json" ]; then
    echo ""
    echo "⚠️  数据文件未找到"
    echo ""
    echo "数据文件应该包含在仓库中。请确认:"
    echo "  1. 你已完整克隆仓库（包括数据文件）"
    echo "  2. 或者查看 README.md 了解如何获取数据"
    echo ""
    echo "所需文件:"
    echo "  - data/startups_classified.json"
    echo "  - data/startups_vectors.json"
else
    echo "✅ 数据文件已就绪"
fi

# 安装 skill
echo ""
echo "📦 安装 Claude Code skill..."

# 检测 Claude Code 技能目录
if [ -d "$HOME/.claude/skills" ]; then
    SKILL_DIR="$HOME/.claude/skills/Think-twice"
else
    SKILL_DIR=".claude/skills/Think-twice"
    mkdir -p .claude/skills
fi

# 复制 skill 文件
mkdir -p "$SKILL_DIR"
cp skill/SKILL.md "$SKILL_DIR/"
echo "✅ Skill 已安装到: $SKILL_DIR"

echo ""
echo "======================"
echo "✅ 安装完成！"
echo ""
echo "使用方法:"
echo "  1. 在 Claude Code 中输入: /Think-twice"
echo "  2. 描述你的创业想法"
echo ""
echo "或者直接运行:"
echo "  python enhanced_analyzer.py 'your startup idea in English'"
echo ""
