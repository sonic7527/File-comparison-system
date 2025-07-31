# 簡單同步腳本
Write-Host "🚀 開始同步程式碼到雲端..." -ForegroundColor Green

Write-Host "📦 添加所有變更..." -ForegroundColor Yellow
git add .

Write-Host "💾 提交變更..." -ForegroundColor Yellow
$commitMessage = "feat: 自動同步 - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git commit -m $commitMessage

Write-Host "☁️ 推送到 GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host "✅ 同步完成！" -ForegroundColor Green
Write-Host "🌐 Streamlit Cloud 將自動部署..." -ForegroundColor Cyan
Write-Host "⏰ 請等待 1-2 分鐘讓雲端部署完成" -ForegroundColor Cyan
Write-Host "🎉 同步流程結束！" -ForegroundColor Green 