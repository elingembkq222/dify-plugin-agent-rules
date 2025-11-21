#!/bin/bash

# 重启前端和后端服务的脚本

echo -e "\n\033[1;36m========================================\033[0m"
echo -e "\033[1;35m🔄        重启 Dify Plugin Agent Rules     🔄\033[0m"
echo -e "\033[1;36m========================================\033[0m"

# 停止服务部分
# 检查并停止后端服务（3001端口）
echo -e "\n\033[1;34m🔍 检查后端服务（3001端口）...\033[0m"
if lsof -i :3001 > /dev/null 2>&1; then
    echo -e "\033[1;33m🛑 停止后端服务...\033[0m"
    lsof -ti :3001 | xargs kill -9
    echo -e "\033[1;32m✅ 后端服务已停止\033[0m"
else
    echo -e "\033[1;32mℹ️  后端服务未运行\033[0m"
fi

# 检查并停止前端服务（5173端口）
echo -e "\n\033[1;34m🔍 检查前端服务（5173端口）...\033[0m"
if lsof -i :5173 > /dev/null 2>&1; then
    echo -e "\033[1;33m🛑 停止前端服务...\033[0m"
    lsof -ti :5173 | xargs kill -9
    echo -e "\033[1;32m✅ 前端服务已停止\033[0m"
else
    echo -e "\033[1;32mℹ️  前端服务未运行\033[0m"
fi

# 等待服务完全停止
sleep 1

# 启动服务部分
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
pip3 install -r requirements.txt

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
echo -e "\033[1;32m🎉 服务重启完成！\033[0m"
echo -e "\033[1;32m- 前端: http://localhost:5173\033[0m"
echo -e "\033[1;32m- 后端: http://localhost:3001\033[0m"
echo -e "\033[1;36m========================================\033[0m"
echo -e "\n\033[1;33m⚠️  停止服务命令: kill $BACKEND_PID $FRONTEND_PID\033[0m"

echo -e "\n\033[1;35m✨ 脚本执行完成！\033[0m"