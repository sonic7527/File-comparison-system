# Hugging Face Spaces 部署檢查清單

## ✅ 已完成的文件

### 核心配置文件
- [x] `huggingface-spaces.yml` - Hugging Face Spaces 配置
- [x] `requirements.txt` - Python 依賴包
- [x] `app.py` - Streamlit 入口文件
- [x] `.streamlit/config.toml` - Streamlit 配置
- [x] `.gitignore` - Git 忽略文件

### 文檔文件
- [x] `README.md` - 專案說明
- [x] `DEPLOYMENT_CHECKLIST.md` - 部署檢查清單

## 🚀 部署步驟

### 1. 準備 Git 倉庫
```bash
# 初始化 Git 倉庫（如果還沒有）
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "準備部署到 Hugging Face Spaces"

# 推送到 GitHub（如果使用 GitHub）
git push origin main
```

### 2. 部署到 Hugging Face Spaces

1. 訪問 [Hugging Face Spaces](https://huggingface.co/spaces)
2. 點擊 "Create new Space"
3. 選擇以下設置：
   - **Owner**: 你的 Hugging Face 用戶名
   - **Space name**: `document-comparison-system` (或你喜歡的名稱)
   - **License**: MIT
   - **SDK**: Streamlit
   - **Space hardware**: CPU (免費) 或 GPU (付費)
4. 點擊 "Create Space"
5. 在 Space 設置中，選擇 "Git-based" 部署方式
6. 連接你的 GitHub 倉庫
7. 設置分支為 `main` 或 `master`

### 3. 自動部署
- Hugging Face 會自動檢測 `huggingface-spaces.yml` 文件
- 系統會自動安裝 `requirements.txt` 中的依賴
- 應用會使用 `app.py` 作為入口文件啟動

## 🔧 故障排除

### 常見問題

1. **依賴安裝失敗**
   - 檢查 `requirements.txt` 中的版本號
   - 確保所有依賴都是公開可用的

2. **應用啟動失敗**
   - 檢查 `app.py` 是否有語法錯誤
   - 確認所有導入的模組都存在

3. **文件路徑問題**
   - 確保所有相對路徑都正確
   - 檢查文件權限設置

### 日誌查看
- 在 Hugging Face Spaces 頁面點擊 "Logs" 查看部署日誌
- 檢查 "Build logs" 和 "Runtime logs"

## 📋 部署後檢查

- [ ] 應用成功啟動
- [ ] 所有功能正常工作
- [ ] 文件上傳功能正常
- [ ] 資料庫操作正常
- [ ] UI 顯示正確

## 🔄 更新部署

每次代碼更新後：
```bash
git add .
git commit -m "更新描述"
git push origin main
```

Hugging Face 會自動檢測更改並重新部署。

## 📞 支援

如果遇到問題：
1. 檢查 Hugging Face Spaces 文檔
2. 查看 Streamlit 部署指南
3. 檢查 GitHub Issues 或創建新的 Issue 