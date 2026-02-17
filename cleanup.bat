@echo off
echo ==========================================
echo 游戏充值网站项目文件清理脚本
echo ==========================================

echo.
echo 正在备份重要文件...
mkdir backup_%date:~0,4%%date:~5,2%%date:~8,2% 2>nul
copy README.md backup_%date:~0,4%%date:~5,2%%date:~8,2% 2>nul
copy requirements.txt backup_%date:~0,4%%date:~5,2%%date:~8,2% 2>nul
copy manage.py backup_%date:~0,4%%date:~5,2%%date:~8,2% 2>nul

echo.
echo 正在清理文档文件...
del "*.md" /q 2>nul
if %errorlevel% neq 0 echo 跳过部分文档文件

echo.
echo 正在清理测试脚本...
del "test_*.py" /q 2>nul
del "*_test.py" /q 2>nul
del "check_*.py" /q 2>nul
del "init_*.py" /q 2>nul
if %errorlevel% neq 0 echo 跳过部分测试脚本

echo.
echo 正在清理临时文件...
del "*.tmp" /q 2>nul
del "*.log" /q 2>nul
del "*.bak" /q 2>nul
del "*~" /q 2>nul

echo.
echo 正在保留必要文件...
move "MAIN_DOCUMENTATION.md" .. 2>nul
move "USER_GUIDE.md" .. 2>nul

echo.
echo 清理完成！
echo ==========================================
echo 重要提醒：
echo 1. 请将 MAIN_DOCUMENTATION.md 和 USER_GUIDE.md 移回项目根目录
echo 2. 检查 docs/ 目录是否需要进一步整理
echo 3. 确认 game_* 目录中的核心文件是否完整
echo ==========================================

pause@echo off
echo ==========================================
echo 游戏充值网站项目文件清理脚本
echo ==========================================

echo.
echo 正在备份重要文件...
mkdir backup_%date:~0,4%%date:~5,2%%date:~8,2% 2>nul
copy README.md backup_%date:~0,4%%date:~5,2%%date:~8,2% 2>nul
copy requirements.txt backup_%date:~0,4%%date:~5,2%%date:~8,2% 2>nul
copy manage.py backup_%date:~0,4%%date:~5,2%%date:~8,2% 2>nul

echo.
echo 正在清理文档文件...
del "*.md" /q 2>nul
if %errorlevel% neq 0 echo 跳过部分文档文件

echo.
echo 正在清理测试脚本...
del "test_*.py" /q 2>nul
del "*_test.py" /q 2>nul
del "check_*.py" /q 2>nul
del "init_*.py" /q 2>nul
if %errorlevel% neq 0 echo 跳过部分测试脚本

echo.
echo 正在清理临时文件...
del "*.tmp" /q 2>nul
del "*.log" /q 2>nul
del "*.bak" /q 2>nul
del "*~" /q 2>nul

echo.
echo 正在保留必要文件...
move "MAIN_DOCUMENTATION.md" .. 2>nul
move "USER_GUIDE.md" .. 2>nul

echo.
echo 清理完成！
echo ==========================================
echo 重要提醒：
echo 1. 请将 MAIN_DOCUMENTATION.md 和 USER_GUIDE.md 移回项目根目录
echo 2. 检查 docs/ 目录是否需要进一步整理
echo 3. 确认 game_* 目录中的核心文件是否完整
echo ==========================================

pause