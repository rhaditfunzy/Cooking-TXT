@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (
    python content_editor.py
) else (
    py -3 content_editor.py
)
if errorlevel 1 (
    echo.
    echo Content Editor tidak dapat dijalankan. Pastikan Python 3 dengan Tkinter terpasang.
    pause
)
endlocal
