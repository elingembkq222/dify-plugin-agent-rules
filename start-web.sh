#!/bin/bash
# 启动web后端server
cd web
node direct-server.js &
# 启动页面
npm run dev &