@echo off
setlocal
cd /d "%~dp0"

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Folder ini belum menjadi Git repository.
    echo Jalankan setup Git dan hubungkan remote GitHub terlebih dahulu.
    exit /b 1
)

git add -A
if errorlevel 1 (
    echo [ERROR] Gagal menambahkan perubahan ke staging area.
    exit /b 1
)

git diff --cached --quiet
if not errorlevel 1 (
    echo Tidak ada perubahan baru untuk dikirim.
    exit /b 0
)

set "COMMIT_MSG=%~1"
if not defined COMMIT_MSG set "COMMIT_MSG=Update Cooking TXT"

git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
    echo [ERROR] Commit gagal. Periksa pesan di atas.
    exit /b 1
)

git push
if errorlevel 1 (
    echo [ERROR] Commit sudah dibuat secara lokal, tetapi push ke GitHub gagal.
    echo Periksa koneksi, login GitHub, dan konfigurasi remote/branch.
    exit /b 1
)

echo.
echo [OK] Perubahan berhasil dikirim ke GitHub.
endlocal
