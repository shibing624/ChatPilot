#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

# 设置默认端口为8080，除非已被定义
PORT="${PORT:-8080}"
export WEBUI_SECRET_KEY="abcdefg123456"

# 打印当前设置的端口和密钥
echo "===================================="
echo " Starting ChatPilot Server"
echo "===================================="
echo "PORT is set to: $PORT"
echo "WEBUI_SECRET_KEY is set to: $WEBUI_SECRET_KEY"
echo "===================================="

# 尝试杀掉之前的聊天服务器实例（如果存在）
# 取消注释的行会杀掉名为 chatpilot 的进程
# echo "Killing existing ChatPilot instances (if any)..."
ps -ef | grep "chatpilot" | grep -v "grep" | awk '{print $2}' | xargs kill -9

# 启动 Gunicorn 服务器，绑定到指定端口
echo "Starting Gunicorn server..."
gunicorn -k uvicorn.workers.UvicornWorker chatpilot.server:app --bind 0.0.0.0:$PORT --forwarded-allow-ips '*' -w 1

# 检查 Gunicorn 启动状态
if [ $? -eq 0 ]; then
    echo "Gunicorn server started successfully on port $PORT"
else
    echo "Failed to start Gunicorn server. Check the logs for details."
    exit 1
fi
