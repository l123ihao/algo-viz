@echo off
cd /d "%~dp0"

python "algo_viz.py"
if not errorlevel 1 goto end

py -3 "algo_viz.py"
if not errorlevel 1 goto end

echo.
echo [Error] Python not found.
echo Please install Python 3 and check "Add Python to PATH" during install.
echo Download: https://www.python.org/downloads/
pause
:end
