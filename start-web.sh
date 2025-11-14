#!/bin/bash
# 启动web后端server
cd web
# 安装依赖（如果需要）
npm install
# 构建前端应用
npm run build
# 启动后端服务
node direct-server.js &
# 启动前端服务器
node server.js &