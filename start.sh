#!/bin/bash

# 启动前端和后端服务的脚本

echo -e "\n\033[1;36m========================================\033[0m"
echo -e "\033[1;35m🚀        启动 Dify Plugin Agent Rules     🚀\033[0m"
echo -e "\033[1;36m========================================\033[0m"

# 检查并停止已在运行的相关进程
echo -e "\n\033[1;34m🔍 检查并停止已在运行的相关进程...\033[0m"

# 检查并停止后端服务（3001端口）
if lsof -i :3001 > /dev/null 2>&1; then
    echo -e "\033[1;33m🛑 停止已在运行的后端服务...\033[0m"
    lsof -ti :3001 | xargs kill -9
fi

# 检查并停止前端服务（5173端口）
if lsof -i :5173 > /dev/null 2>&1; then
    echo -e "\033[1;33m🛑 停止已在运行的前端服务...\033[0m"
    lsof -ti :5173 | xargs kill -9
fi

# 启动后端服务
echo -e "\n\033[1;34m⚙️  启动后端服务...\033[0m"
cd web && node direct-server.js > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "\033[1;32m✅ 后端服务已启动，PID: $BACKEND_PID\033[0m"
echo -e "\033[1;32m📝 后端服务日志将输出到: ../logs/backend.log\033[0m"
echo -e "\033[1;32m🌐 后端服务运行在: http://localhost:3001\033[0m"

# 等待后端服务启动
sleep 2

# 启动前端服务
echo -e "\n\033[1;34m⚙️  启动前端服务...\033[0m"
cd web && npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "\033[1;32m✅ 前端服务已启动，PID: $FRONTEND_PID\033[0m"
echo -e "\033[1;32m📝 前端服务日志将输出到: ../logs/frontend.log\033[0m"
echo -e "\033[1;32m🌐 前端服务运行在: http://localhost:5173\033[0m"

echo -e "\n\033[1;36m========================================\033[0m"
echo -e "\033[1;32m🎉 服务启动完成！\033[0m"
echo -e "\033[1;32m- 前端: http://localhost:5173\033[0m"
echo -e "\033[1;32m- 后端: http://localhost:3001\033[0m"
echo -e "\033[1;36m========================================\033[0m"
echo -e "\n\033[1;33m⚠️  停止服务命令: kill $BACKEND_PID $FRONTEND_PID\033[0m"

# 自动打开浏览器功能
echo -e "\n\033[1;34m⏳ 正在等待服务完全启动...\033[0m"
sleep 3  # 额外等待以确保服务完全就绪

# 检查系统类型，使用适当的命令打开浏览器
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo -e "\033[1;32m🌐 正在打开浏览器...\033[0m"
    open http://localhost:5173
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo -e "\033[1;32m🌐 正在打开浏览器...\033[0m"
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:5173
    elif command -v gnome-open &> /dev/null; then
        gnome-open http://localhost:5173
    else
        echo -e "\033[1;33m⚠️  无法自动打开浏览器，请手动访问 http://localhost:5173\033[0m"
    fi
elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win32" ]]; then
    # Windows
    echo -e "\033[1;32m🌐 正在打开浏览器...\033[0m"
    start http://localhost:5173
else
    echo -e "\033[1;33m⚠️  无法自动打开浏览器，请手动访问 http://localhost:5173\033[0m"
fi

echo -e "\n\033[1;35m✨ 脚本执行完成！\033[0m"