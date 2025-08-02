# 貢獻指南

感謝您對北大文件比對與範本管理系統的關注！

## 🤝 如何貢獻

### 報告問題
如果您發現了問題，請：
1. 檢查是否已經有相關的 Issue
2. 創建新的 Issue，並詳細描述問題
3. 提供重現步驟和錯誤信息

### 提交代碼
1. Fork 這個專案
2. 創建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

## 📋 開發環境設置

### 本地開發
```bash
# 克隆專案
git clone https://github.com/sonic7527/File-comparison-system.git
cd File-comparison-system

# 安裝依賴
pip install -r requirements.txt

# 運行應用
streamlit run main.py
```

### 代碼風格
- 使用 Python 3.9+
- 遵循 PEP 8 代碼風格
- 添加適當的註釋和文檔

## 🎯 功能開發指南

### 新功能開發
1. 在 `views/` 目錄下創建新的頁面文件
2. 在 `core/` 目錄下添加核心邏輯
3. 更新 `app.py` 或 `streamlit_app.py` 添加路由
4. 更新 `README.md` 文檔

### 測試
- 確保所有功能正常工作
- 測試不同瀏覽器和設備
- 驗證文件上傳和下載功能

## 📝 提交信息規範

使用清晰的提交信息：
- `feat:` 新功能
- `fix:` 修復問題
- `docs:` 文檔更新
- `style:` 代碼格式調整
- `refactor:` 代碼重構
- `test:` 測試相關
- `chore:` 構建過程或輔助工具的變動

## 📞 聯繫方式

如有問題，請通過以下方式聯繫：
- 創建 GitHub Issue
- 發送郵件至專案維護者

感謝您的貢獻！🎉 