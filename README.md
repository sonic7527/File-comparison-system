# 📄 PDF文件比對與範本管理系統

一個專為文件處理設計的智能系統，支援PDF範本管理、變數標記、文件生成與比對功能。

## ✨ 主要功能

### 🎨 PDF變數標記
* 上傳多頁PDF檔案作為範本
* 視覺化標記變數欄位
* 支援變數頁面與參考資料頁面分類
* 可編輯已標記的變數

### 📝 檔案輸入與生成
* 根據標記範本填入變數值
* 生成與範本一致的新檔案
* 維持格式一致性

### 🔍 文件比對檢查
* 多範本比對支援（3-5個範本對應一種情況）
* 精確變數比對與相似度檢查
* 自動區分變數頁面與參考資料

### ⚙️ 範本管理設定
* 範本資訊管理
* 頁面類型設定
* 系統設定調整

### 📄 智能文件生成系統（新功能）
* **基本資料群組管理**：定義一組固定的輸入欄位
* **範本群組管理**：基於基本資料群組創建不同格式範本
* **A4格式支援**：自動轉換為A4直式或橫式格式
* **圖片轉換**：支援圖片轉Excel/Word格式
* **群組化工作流程**：選擇範本群組 → 自動載入輸入頁面 → 填入資料 → 生成文件

## 🚀 快速開始

### 本地開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動應用
streamlit run main.py
```

### 雲端部署

本系統已針對 Streamlit Cloud 優化，支援一鍵部署。

**線上版本**：https://bei-da-pdf-comparison.streamlit.app

## 🔄 開發工作流程

### 本地開發 + GitHub 同步

1. **本地開發**：
   ```bash
   # 在本地進行開發
   streamlit run main.py
   ```

2. **同步到 GitHub**：
   ```bash
   git add .
   git commit -m "功能描述"
   git push origin main
   ```

3. **自動部署**：
   - GitHub 同步後，Streamlit Cloud 會自動重新部署
   - 線上版本會自動更新

4. **手機編輯**：
   - 可以使用 GitHub 網頁版編輯檔案
   - 或使用 Cursor Web 版本

## 🛠️ 技術架構

* **前端**: Streamlit
* **PDF處理**: PyMuPDF + pdf2image（備用）
* **資料庫**: SQLite
* **圖像處理**: Pillow
* **互動標記**: streamlit-drawable-canvas
* **Excel處理**: openpyxl, xlrd
* **Word處理**: python-docx

## 📦 依賴套件

```
streamlit==1.47.1
pandas==2.3.1
pillow==11.3.0
pdf2image==1.17.0
PyMuPDF==1.25.3
streamlit-drawable-canvas==0.8.0
openpyxl==3.1.2
xlrd==2.0.1
python-docx==1.2.0
```

## 🔧 環境需求

* Python 3.7+
* 現代網頁瀏覽器
* 支援雲端部署（Streamlit Cloud、Render、Railway等）

## 📂 專案結構

```
document-comparison-system/
├── main.py                    # 主程式入口
├── requirements.txt           # 依賴套件
├── .streamlit/config.toml     # Streamlit設定
├── pages/                     # 功能頁面
│   ├── home_page.py          # 首頁
│   ├── pdf_annotation_interface.py  # PDF標記
│   ├── file_input_generator.py      # 檔案生成
│   ├── document_generator.py        # 智能文件生成
│   └── template_settings.py         # 範本設定
├── core/                      # 核心邏輯
│   └── pdf_annotation_system.py    # PDF處理系統
├── utils/                     # 工具函數
│   └── ui_components.py      # UI組件
└── data/                      # 資料儲存
```

## 🌟 特色

* ✅ 多人同時使用
* ✅ 雲端部署支援
* ✅ 自動錯誤恢復
* ✅ 直觀的使用者介面
* ✅ 完整的中文支援
* ✅ 群組化文件管理
* ✅ A4格式自動轉換
* ✅ 圖片轉文件功能

## 📝 授權

本專案採用 MIT 授權條款。

---

**系統版本**: v3.0 (群組化版本)  
**最後更新**: 2024