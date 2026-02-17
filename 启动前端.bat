@echo off
echo ==========================================
echo 游戏充值网站 - 前端服务器启动脚本
echo ==========================================

echo.
echo 正在启动 Vue 前端服务器...
echo.

cd /d "e:\小程序开发\游戏充值网站\frontend"

if not exist "node_modules" (
    echo 警告：未找到 node_modules 目录
    echo 正在安装依赖...
    call npm install
)

echo.
echo 启动前端开发服务器...
echo.
echo ==========================================
echo 前端页面地址: http://localhost:5176/
echo ==========================================
echo.
echo 按 Ctrl+C 可停止服务器
echo.

call npm run dev

pause