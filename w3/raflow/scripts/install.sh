#!/bin/bash

# Raflow 安装脚本
# 用于构建后自动签名并安装到 /Applications

set -e

APP_NAME="Raflow"
BUNDLE_PATH="src-tauri/target/release/bundle/macos/${APP_NAME}.app"
INSTALL_PATH="/Applications/${APP_NAME}.app"

echo "🔧 Raflow 安装脚本"
echo "================================"

# 检查构建产物是否存在
if [ ! -d "$BUNDLE_PATH" ]; then
    echo "❌ 错误: 找不到构建产物 $BUNDLE_PATH"
    echo "请先运行 'npm run tauri:build'"
    exit 1
fi

# 关闭正在运行的 Raflow
echo "📦 关闭旧版本..."
killall "$APP_NAME" 2>/dev/null || true
sleep 1

# 删除旧版本
echo "🗑️  删除旧版本..."
rm -rf "$INSTALL_PATH" 2>/dev/null || true

# 复制新版本
echo "📋 复制新版本到 /Applications..."
cp -r "$BUNDLE_PATH" "$INSTALL_PATH"

# 重新签名（确保 ad-hoc 签名正确）
echo "🔐 签名应用..."
codesign --force --deep --sign - "$INSTALL_PATH"

# 验证签名
echo "✅ 验证签名..."
codesign --verify --verbose "$INSTALL_PATH"

echo ""
echo "================================"
echo "✅ 安装完成！"
echo ""
echo "⚠️  首次安装需要授予辅助功能权限："
echo "   系统设置 → 隐私与安全性 → 辅助功能 → 添加 Raflow"
echo ""
echo "🚀 启动 Raflow..."
open "$INSTALL_PATH"

echo "================================"
echo "按 Cmd+Shift+\\ 开始录音"
