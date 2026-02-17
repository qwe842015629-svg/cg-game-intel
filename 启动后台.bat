@echo off
echo ==========================================
echo 游戏充值网站 - 后台服务器启动脚本
echo ==========================================

echo.
echo 正在启动 Django 后台服务器...
echo.

cd /d "e:\小程序开发\游戏充值网站"

if not exist "venv\Scripts\activate.bat" (
    echo 错误：未找到虚拟环境！
    echo 请先运行：python -m venv venv
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo 虚拟环境已激活
echo.
echo 启动 Django 服务器...
echo.
echo ==========================================
echo 后台管理地址: http://127.0.0.1:8000/admin/
echo API 地址: http://127.0.0.1:8000/api/
echo ==========================================
echo.
echo 按 Ctrl+C 可停止服务器
echo.

python manage.py runserver

pause