# 🌐 Turso + GitHub 雲端部署指南

## 問題背景
Streamlit Cloud 使用**暫時性檔案系統 (Ephemeral Filesystem)**，每次重新部署時所有本地檔案都會被清除。

## 🚀 解決方案：Turso + GitHub

### 架構設計
- **資料庫記錄** → Turso SQLite
- **範本檔案** → GitHub 倉庫
- **本地開發** → SQLite + 本地檔案

## 📋 部署步驟

### 步驟 1：創建 Turso 資料庫

1. 前往 [Turso](https://turso.tech/)
2. 註冊/登入帳號
3. 創建新資料庫
4. 獲取資料庫 URL 和 Auth Token

### 步驟 2：配置 GitHub

1. 創建 GitHub Personal Access Token
   - 前往 GitHub Settings → Developer settings → Personal access tokens
   - 創建新 token，勾選 `repo` 權限
2. 在您的 GitHub 倉庫中創建 `templates/` 資料夾

### 步驟 3：配置 Streamlit Secrets

在 Streamlit Cloud 的專案設定中，找到 "Secrets" 選項，添加：

```toml
[turso]
url = "libsql://your-database-name.turso.io"
token = "your-turso-auth-token"

[github]
token = "your-github-personal-access-token"
owner = "your-github-username"
repo = "your-repository-name"
```

### 步驟 4：創建資料庫表格

Turso 會自動創建表格，但您也可以在 Turso Dashboard 中手動執行：

```sql
CREATE TABLE IF NOT EXISTS comparison_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 本地開發

### 使用本地模式（開發時）
- 不需要配置 Turso 和 GitHub
- 資料會保存在 `data/templates.db`
- 檔案保存在 `data/comparison_templates/`

### 使用雲端模式（測試）
1. 複製 `.streamlit/secrets.toml.example` 為 `.streamlit/secrets.toml`
2. 填入您的 Turso 和 GitHub 配置
3. 重新啟動應用程序

## 📊 功能特點

### ✅ 優勢
1. **資料持久化**：範本資料不會因為重新部署而丟失
2. **檔案存儲**：範本檔案存儲在 GitHub，可版本控制
3. **自動同步**：本地新增範本時自動同步到雲端
4. **雙重備份**：本地 + 雲端雙重保護
5. **免費額度**：Turso 免費 1GB，GitHub 免費存儲

### 🔄 同步策略
- **本地新增** → 自動同步到 Turso + GitHub
- **雲端查詢** → 優先從 Turso 讀取
- **檔案下載** → 從 GitHub 下載到臨時目錄

## 🎯 容量監控

系統會分別顯示：
- **本地容量**：本地 SQLite 中的範本統計
- **雲端容量**：Turso 中的範本統計
- **檔案存儲**：GitHub 中的檔案統計

## 🔍 故障排除

### 問題：無法連接到 Turso
**解決方案**：
1. 檢查 secrets 配置是否正確
2. 確認 Turso 資料庫是否啟用
3. 檢查網路連接

### 問題：GitHub 上傳失敗
**解決方案**：
1. 檢查 GitHub token 權限
2. 確認倉庫名稱和所有者
3. 檢查 `templates/` 資料夾是否存在

### 問題：檔案下載失敗
**解決方案**：
1. 檢查 GitHub 檔案 URL 是否正確
2. 確認檔案是否已上傳到 GitHub
3. 檢查網路連接

## 📈 性能優化

1. **連接池**：Turso 自動管理連接
2. **快取機制**：本地查詢優先
3. **異步上傳**：檔案上傳不阻塞界面
4. **錯誤處理**：雲端失敗不影響本地功能 