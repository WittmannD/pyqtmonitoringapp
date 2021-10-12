@echo off
cd client & npm run build && ^
cd .. & pyinstaller main.spec -y -icon=app.ico && ^
dist\main\main.exe
pause
