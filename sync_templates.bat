@echo off
chcp 65001 >nul
echo ========================================
echo 北大文件比對系統 - 範本同步工具
echo ========================================
echo.

:menu
echo 請選擇操作：
echo 1. 添加新範本到本地
echo 2. 同步所有範本到雲端
echo 3. 查看當前狀態
echo 4. 退出
echo.
set /p choice="請輸入選項 (1-4): "

if "%choice%"=="1" goto add_template
if "%choice%"=="2" goto sync_to_cloud
if "%choice%"=="3" goto check_status
if "%choice%"=="4" goto exit
goto menu

:add_template
echo.
echo 請將您的範本文件複製到以下目錄：
echo - Excel 欄位定義: data\excel\
echo - Word/Excel 範本: data\templates\
echo - Excel 範本: data\excel_templates\
echo.
pause
goto menu

:sync_to_cloud
echo.
echo 正在同步範本到雲端...
git add data/excel/*.xlsx
git add data/templates/*.xlsx
git add data/templates/*.docx
git add data/excel_templates/*.xlsx
git commit -m "Update templates"
git push origin main
echo.
echo ✅ 同步完成！Streamlit Cloud 將在幾分鐘內自動重新部署
echo.
pause
goto menu

:check_status
echo.
echo 當前 Git 狀態：
git status --porcelain
echo.
echo 本地範本文件：
if exist "data\excel" (
    echo Excel 欄位定義:
    dir /b "data\excel\*.xlsx" 2>nul
)
if exist "data\templates" (
    echo Word/Excel 範本:
    dir /b "data\templates\*.*" 2>nul
)
if exist "data\excel_templates" (
    echo Excel 範本:
    dir /b "data\excel_templates\*.xlsx" 2>nul
)
echo.
pause
goto menu

:exit
echo 再見！
pause 