#!/usr/bin/env bash

# Commitizen 便捷脚本
# 使用方法: ./commit.sh 或 ./commit.sh check

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.cz.toml"

# 确保配置文件存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 找不到配置文件 .cz.toml"
    exit 1
fi

# 根据参数执行不同操作
case "$1" in
    "check")
        echo "验证提交消息格式..."
        uv run cz --config "$CONFIG_FILE" check --rev-range HEAD~1..HEAD
        ;;
    "example")
        echo "提交消息示例:"
        uv run cz --config "$CONFIG_FILE" example
        ;;
    "schema")
        echo "提交消息格式规范:"
        uv run cz --config "$CONFIG_FILE" schema
        ;;
    "info")
        uv run cz --config "$CONFIG_FILE" info
        ;;
    "help"|"-h"|"--help")
        echo "使用方法:"
        echo "  $0        # 交互式提交"
        echo "  $0 check  # 验证最近的提交消息"
        echo "  $0 example # 查看提交消息示例"
        echo "  $0 schema  # 查看提交消息格式规范"
        echo "  $0 info    # 查看配置信息"
        echo "  $0 help    # 显示此帮助信息"
        ;;
    "")
        # 默认执行交互式提交
        uv run cz --config "$CONFIG_FILE" commit
        ;;
    *)
        echo "未知参数: $1"
        echo "使用 $0 help 查看帮助信息"
        exit 1
        ;;
esac
