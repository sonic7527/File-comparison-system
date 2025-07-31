# 同步到雲端腳本
Write-Host "🚀 開始同步程式碼到雲端..." -ForegroundColor Green

# 檢查 Git 狀態（使用簡化命令）
Write-Host "📋 檢查變更狀態..." -ForegroundColor Yellow
try {
    $status = git status --porcelain 2>$null
    if ($status) {
        Write-Host "✅ 發現變更，準備提交..." -ForegroundColor Green
        
        # 添加所有變更
        Write-Host "📦 添加變更到暫存區..." -ForegroundColor Yellow
        git add . 2>$null
        
        # 提交變更
        Write-Host "💾 提交變更..." -ForegroundColor Yellow
        $commitMessage = "feat: 自動同步 - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        git commit -m $commitMessage 2>$null
        
        # 推送到 GitHub
        Write-Host "☁️ 推送到 GitHub..." -ForegroundColor Yellow
        git push origin main 2>$null
        
        Write-Host "✅ 同步完成！" -ForegroundColor Green
        Write-Host "🌐 Streamlit Cloud 將自動部署..." -ForegroundColor Cyan
        Write-Host "⏰ 請等待 1-2 分鐘讓雲端部署完成" -ForegroundColor Cyan
    } else {
        Write-Host "ℹ️ 沒有新的變更需要同步" -ForegroundColor Blue
    }
} catch {
    Write-Host "❌ 同步過程中發生錯誤: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "🎉 同步流程結束！" -ForegroundColor Green 