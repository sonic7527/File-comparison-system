# 🚀 部署步驟指南（20分鐘完成）

## 📤 步驟一：GitHub 準備

### 1. 建立 GitHub 帳號
- 前往 https://github.com/
- 點擊 "Sign up" 註冊（如果已有帳號請直接登入）

### 2. 建立新倉庫
1. 登入後點擊右上角的 "+" → "New repository"
2. 填寫資訊：
   ```
   Repository name: document-comparison-system
   Description: PDF文件比對與範本管理系統
   選擇: Public（公開）
   ✅ Add a README file
   ```
3. 點擊 "Create repository"

### 3. 上傳專案檔案
**方式A：網頁拖拽上傳（推薦）**
1. 在新建的倉庫頁面，點擊 "uploading an existing file"
2. 選擇要上傳的檔案：
   ```
   必須上傳的檔案：
   ✅ main.py
   ✅ requirements.txt
   ✅ README.md
   ✅ .gitignore
   ✅ 整個 pages/ 資料夾
   ✅ 整個 core/ 資料夾  
   ✅ 整個 utils/ 資料夾
   ✅ 整個 .streamlit/ 資料夾
   ```
3. 填寫提交訊息："Initial commit - PDF文件比對系統"
4. 點擊 "Commit changes"

## ☁️ 步驟二：Streamlit Cloud 部署

### 1. 前往 Streamlit Cloud
- 開啟 https://share.streamlit.io/
- 點擊右上角 "Sign up" 
- 選擇 "Continue with GitHub"（用 GitHub 帳號登入）

### 2. 授權 Streamlit
- 授權 Streamlit 存取您的 GitHub 帳號
- 允許讀取您的倉庫

### 3. 部署應用
1. 登入後點擊 "New app"
2. 填寫部署資訊：
   ```
   Repository: 您的GitHub用戶名/document-comparison-system
   Branch: main
   Main file path: main.py
   App URL (optional): 可自訂，例如 pdf-comparison
   ```
3. 點擊 "Deploy!"

### 4. 等待部署完成
- ⏰ 首次部署約需 3-5 分鐘
- 📦 系統會自動安裝 requirements.txt 中的套件
- ✅ 部署成功後會顯示您的應用網址

## 🎉 完成！

### 您的系統現在可以：
- 🌐 **固定網址**：`https://您的用戶名-document-comparison-system-main-xxx.streamlit.app`
- 👥 **多人使用**：任何人都可以透過網址訪問
- 🔄 **自動更新**：GitHub 更新後自動重新部署
- ⚡ **24/7運行**：您的電腦可以關機

### 如果遇到問題：
1. 確認所有必要檔案都已上傳到 GitHub
2. 檢查 requirements.txt 格式是否正確
3. 查看 Streamlit Cloud 的部署日誌錯誤訊息

---

**預計完成時間：15-20分鐘**  
**部署成功後，請分享您的應用網址！** 🎊