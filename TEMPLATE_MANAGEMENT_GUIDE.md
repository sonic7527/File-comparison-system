# 📁 範本管理使用指南

## 🎯 解決方案概述

您現在有兩種方式管理範本：

### 方案一：本地開發 + 雲端同步（推薦）

**優點：**
- ✅ 可以在本地測試和開發
- ✅ 快速迭代和修改
- ✅ 一鍵同步到雲端
- ✅ 保持版本控制

**工作流程：**
1. 在本地創建/修改範本
2. 使用 `sync_templates.bat` 同步到雲端
3. Streamlit Cloud 自動重新部署

### 方案二：雲端直接上傳

**優點：**
- ✅ 即時生效
- ✅ 不需要本地環境

**缺點：**
- ❌ 無法在本地測試
- ❌ 修改較麻煩

## 🛠️ 本地範本管理工具

### 快速同步工具

運行 `sync_templates.bat` 來使用圖形化工具：

```bash
# 雙擊運行或在命令行執行
sync_templates.bat
```

### 手動操作步驟

1. **添加新範本**：
   ```bash
   # 將範本文件複製到對應目錄
   copy "您的範本.xlsx" "data\excel\"
   copy "您的範本.docx" "data\templates\"
   ```

2. **同步到雲端**：
   ```bash
   git add data/excel/*.xlsx
   git add data/templates/*.xlsx
   git add data/templates/*.docx
   git commit -m "Add new templates"
   git push origin main
   ```

3. **查看狀態**：
   ```bash
   git status
   dir data\excel\
   dir data\templates\
   ```

## 📂 目錄結構說明

```
data/
├── excel/           # Excel 欄位定義文件
│   └── 基本資料.xlsx
├── templates/       # Word/Excel 範本文件
│   └── 工程設計監造委託書.xlsx
├── excel_templates/ # Excel 範本文件
└── uploaded_excel/  # 用戶上傳的文件（自動生成）
```

## 🔄 同步流程

1. **本地開發**：
   - 在本地創建/修改範本
   - 使用 `streamlit run main.py` 測試
   - 確認功能正常

2. **同步到雲端**：
   - 運行 `sync_templates.bat`
   - 選擇 "同步所有範本到雲端"
   - 等待 Streamlit Cloud 重新部署

3. **驗證部署**：
   - 訪問 https://file-comparison-system-beida.streamlit.app/
   - 確認範本已更新

## 🚀 最佳實踐

### 範本命名規範
- 使用中文名稱，清楚描述用途
- 避免特殊字符和空格
- 例如：`工程設計監造委託書.xlsx`

### 版本控制
- 每次修改範本後立即同步
- 使用有意義的提交信息
- 定期備份重要範本

### 測試流程
1. 本地測試 → 2. 同步到雲端 → 3. 雲端驗證

## 🆘 常見問題

### Q: 同步後雲端沒有更新？
A: 等待 2-5 分鐘，Streamlit Cloud 需要時間重新部署

### Q: 範本上傳失敗？
A: 檢查文件格式是否支援（.xlsx, .docx, .xls, .doc）

### Q: Git 操作失敗？
A: 確保已正確設置 Git 憑證和遠程倉庫

### Q: 本地測試失敗？
A: 確保已安裝所有依賴：`pip install -r requirements.txt`

## 📞 支援

如果遇到問題，請：
1. 檢查錯誤信息
2. 確認文件格式和路徑
3. 查看 Git 狀態
4. 聯繫技術支援 