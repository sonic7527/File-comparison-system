@echo off
echo 🚀 開始同步程式碼到雲端...
echo.
echo 📦 添加所有變更...
git add .
echo.
echo 💾 提交變更...
git commit -m "feat: 自動同步 - %date% %time%"
echo.
echo ☁️ 推送到 GitHub...
git push origin main
echo.
echo ✅ 同步完成！
echo 🌐 Streamlit Cloud 將自動部署...
echo ⏰ 請等待 1-2 分鐘讓雲端部署完成
echo.
pause 