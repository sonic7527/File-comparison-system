# Streamlit Cloud Secrets 配置指南

## 問題描述
在 Streamlit Cloud 部署中，應用程式無法正確連接到 Turso 雲端資料庫，顯示"未配置 Turso，將使用本地 SQLite"的警告。

## 解決方案

### 1. 在 Streamlit Cloud 中配置 Secrets

1. 登入 [Streamlit Cloud](https://share.streamlit.io/)
2. 找到你的應用程式：`file-comparison-system-beida`
3. 點擊 "Settings" 標籤
4. 在 "Secrets" 部分，添加以下配置：

```toml
[turso]
url = "libsql://your-database-name.turso.io"
token = "your-turso-token"
```

### 2. 獲取 Turso 配置信息

#### 獲取 Turso URL：
```bash
turso db show your-database-name --url
```

#### 獲取 Turso Token：
```bash
turso db tokens create your-database-name
```

### 3. 本地測試 Secrets

如果你想要在本地測試 secrets 配置，可以創建 `.streamlit/secrets.toml` 文件：

```toml
[turso]
url = "libsql://your-database-name.turso.io"
token = "your-turso-token"
```

**注意**：不要將包含真實 token 的 secrets.toml 文件提交到 Git！

### 4. 驗證配置

部署後，應用程式會在主頁面顯示 Turso 狀態：
- ✅ Turso 雲端資料庫已配置
- ⚠️ 未配置 Turso，將使用本地 SQLite

### 5. 常見問題

#### Q: 為什麼本地測試正常，但部署後無法連接？
A: Streamlit Cloud 環境中的 secrets 管理與本地不同，需要通過 Streamlit Cloud 的 web 界面配置。

#### Q: 如何檢查 secrets 是否正確配置？
A: 可以暫時使用 `test_secrets.py` 文件來檢查 secrets 結構。

#### Q: 如果配置了 secrets 但仍然顯示本地模式？
A: 檢查：
1. secrets 格式是否正確（TOML 格式）
2. URL 和 token 是否有效
3. 網絡連接是否正常

### 6. 測試步驟

1. 配置 Streamlit Cloud secrets
2. 重新部署應用程式
3. 檢查主頁面的 Turso 狀態顯示
4. 測試文件上傳功能
5. 確認數據保存到雲端

## 技術細節

### Secrets 結構
```toml
[turso]
url = "libsql://database-name.turso.io"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 代碼中的檢查邏輯
```python
# 從 Streamlit secrets 獲取配置
turso_url = st.secrets.get("turso", {}).get("url")
turso_token = st.secrets.get("turso", {}).get("token")

# 如果無法從 secrets 獲取，嘗試從環境變數獲取
if not turso_url:
    turso_url = os.environ.get("TURSO_URL")
if not turso_token:
    turso_token = os.environ.get("TURSO_TOKEN")
```

## 注意事項

1. **安全性**：不要在代碼中硬編碼 secrets
2. **備份**：定期備份 Turso 數據庫
3. **監控**：監控應用程式的連接狀態
4. **測試**：在本地和雲端都進行充分測試 