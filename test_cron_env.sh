#!/bin/bash

# 测试crontab环境的脚本
# 用法: ./test_cron_env.sh

echo "=== Crontab 环境测试 ==="
echo "时间: $(date)"
echo "工作目录: $(pwd)"
echo "用户: $(whoami)"
echo ""

echo "=== PATH 环境变量 ==="
echo "PATH: $PATH"
echo ""

echo "=== Claude 相关环境变量 ==="
echo "ANTHROPIC_BASE_URL: $ANTHROPIC_BASE_URL"
echo "NODE_EXTRA_CA_CERTS: $NODE_EXTRA_CA_CERTS"
echo ""

echo "=== 检查 Claude 命令 ==="
if command -v claude &> /dev/null; then
    echo "✓ claude 命令可用: $(which claude)"
    echo "版本信息:"
    claude --version 2>&1 || echo "  无法获取版本信息"
else
    echo "✗ claude 命令不可用"
    echo "  尝试使用绝对路径:"
    if [ -f "/opt/homebrew/bin/claude" ]; then
        echo "  ✓ 找到: /opt/homebrew/bin/claude"
    else
        echo "  ✗ 未找到: /opt/homebrew/bin/claude"
    fi
fi
echo ""

echo "=== 检查 Python 虚拟环境 ==="
if [ -d "venv" ]; then
    echo "✓ venv 目录存在"
    if [ -f "venv/bin/activate" ]; then
        echo "✓ activate 脚本存在"
        source venv/bin/activate
        echo "✓ 虚拟环境已激活"
        echo "  Python路径: $(which python3)"
        echo "  Python版本: $(python3 --version)"
    else
        echo "✗ activate 脚本不存在"
    fi
else
    echo "✗ venv 目录不存在"
fi
echo ""

echo "=== 检查配置文件 ==="
files=("config.yml" "mcp.json" "ai_prompt.md")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file 存在"
    else
        echo "✗ $file 不存在"
    fi
done
echo ""

echo "=== 检查 Python 脚本 ==="
scripts=("getrecentchatlogs.py" "analyze_logs.py" "post_wechat.py")
for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        echo "✓ $script 存在"
    else
        echo "✗ $script 不存在"
    fi
done
echo ""

echo "=== 测试简单的 Claude 调用 ==="
# 设置环境变量
export PATH="/opt/homebrew/bin:$PATH"
export ANTHROPIC_BASE_URL="https://gaccode.com/claudecode"
export NODE_EXTRA_CA_CERTS="/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/ca.pem"

echo "测试 Claude 响应..."
if echo "简单测试：请回复'测试成功'" | /opt/homebrew/bin/claude 2>&1; then
    echo "✓ Claude 调用成功"
else
    echo "✗ Claude 调用失败"
fi

echo ""
echo "=== 测试完成 ==="