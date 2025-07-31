# 📱 修正版上傳內容

## 🎯 需要更新的檔案

### 📁 檔案1：`main.py`
**修正：移除重複的標題**

### 📁 檔案2：`pages/home_page.py`  
**修正：改為"歡迎使用北大文件比對與範本管理系統"並調整字體大小**

### 📁 檔案3：`utils/ui_components.py`
**修正：調整手機端字體大小避免斷行**

---

## 🚀 上傳步驟

### 第一步：更新 `main.py`
1. 前往GitHub倉庫
2. 點擊 `main.py`
3. 點擊 ✏️ 編輯
4. 找到第271-275行：
```python
    # 啟用響應式設計
    apply_custom_css()
    
    st.title("📄 PDF文件比對與範本管理系統")
    st.markdown("---")
```
5. 替換為：
```python
    # 啟用響應式設計
    apply_custom_css()
```
6. 提交：`Fix duplicate title issue`

### 第二步：更新 `pages/home_page.py`
1. 點擊 `pages/home_page.py`
2. 點擊 ✏️ 編輯
3. 找到第11-16行：
```python
    <div class="mobile-toolbar">
        <h1>📄 PDF文件比對系統</h1>
        <div class="mobile-status">✅ 系統正常運行</div>
    </div>
```
4. 替換為：
```python
    <div class="mobile-toolbar">
        <h1 style="font-size: 1.8rem; line-height: 1.2; margin: 0.5rem 0;">📄 歡迎使用北大文件比對與範本管理系統</h1>
        <div class="mobile-status">✅ 系統正常運行</div>
    </div>
```
5. 提交：`Update title to 北大 and fix font size`

### 第三步：更新 `utils/ui_components.py`
1. 點擊 `utils/ui_components.py`
2. 點擊 ✏️ 編輯
3. 找到第23-28行：
```css
        h1 { 
            font-size: 2.2rem !important; 
            line-height: 1.1 !important; 
            margin-bottom: 1rem !important;
            text-align: center !important;
        }
```
4. 替換為：
```css
        h1 { 
            font-size: 1.8rem !important; 
            line-height: 1.2 !important; 
            margin-bottom: 1rem !important;
            text-align: center !important;
        }
```
5. 提交：`Fix mobile font size to prevent line breaks`

---

## ✅ 修正結果

- ❌ 移除重複標題
- ✅ 顯示"歡迎使用北大文件比對與範本管理系統"
- ✅ 調整字體大小避免斷行
- ✅ 保持手機優化效果

**3-5分鐘後就能看到修正效果！** 🎉