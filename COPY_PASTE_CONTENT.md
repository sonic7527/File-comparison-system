# 📋 手動創建檔案內容

## 📄 .gitignore 檔案內容
```
# 虛擬環境
venv/
env/
.venv/

# Python 快取檔案
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# IDE 設定檔
.vscode/
.idea/
*.swp
*.swo

# 系統檔案
.DS_Store
Thumbs.db

# 臨時檔案
temp/
tmp/
*.tmp

# 日誌檔案
*.log

# 本地資料庫（可選，如果想保留請移除此行）
# data/*.db

# Poppler 工具（雲端不需要）
poppler-*/

# 專案相關的臨時檔案
project_structure.txt
deployment_guide.md
streamlit_cloud_setup.md
github_upload_guide.md

# 輸出目錄
outputs/
uploads/
templates/

# 不必要的配置目錄
config/
gui/
assets/
components/
```

## ⚙️ .streamlit/config.toml 檔案內容
```
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[client]
showErrorDetails = false

[server]
headless = true
enableCORS = false
enableXsrfProtection = false
```