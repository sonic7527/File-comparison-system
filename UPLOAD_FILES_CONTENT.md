# 📱 手機優化檔案上傳內容

## 🎯 上傳步驟

1. 前往您的GitHub倉庫
2. 依序更新以下檔案
3. 等待自動部署完成

---

## 📁 檔案1：`utils/ui_components.py`

**步驟：**
1. 點擊倉庫中的 `utils/ui_components.py`
2. 點擊 ✏️ 編輯按鈕
3. 選擇所有內容並刪除
4. 複製下方內容並貼上
5. 提交：`Update mobile UI optimization`

**檔案內容：**
```python
"""UI 組件模組 - 響應式設計版本"""
import streamlit as st
from datetime import datetime

def apply_custom_css():
    """套用專為手機優化的CSS樣式"""
    st.markdown("""
    <style>
    /* 基礎響應式設計 */
    .main .block-container {
        padding: 1rem;
        max-width: 1200px;
    }
    
    /* 手機端深度優化 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.3rem !important;
            margin: 0 !important;
        }
        
        /* 大字體，易讀性 */
        h1 { 
            font-size: 2.2rem !important; 
            line-height: 1.1 !important; 
            margin-bottom: 1rem !important;
            text-align: center !important;
        }
        h2 { 
            font-size: 1.6rem !important; 
            line-height: 1.2 !important; 
            margin: 1rem 0 !important;
        }
        h3 { 
            font-size: 1.3rem !important; 
            line-height: 1.3 !important; 
            margin: 0.8rem 0 !important;
        }
        
        /* 大按鈕，易點擊 */
        .stButton > button {
            width: 100% !important;
            height: 3.5rem !important;
            margin: 0.5rem 0 !important;
            padding: 1rem !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
            border-radius: 8px !important;
        }
        
        /* 側邊欄優化 */
        .css-1d391kg {
            width: 250px !important;
        }
        
        /* 選擇框優化 */
        .stSelectbox {
            margin: 0.5rem 0 !important;
        }
        
        .stSelectbox > div > div {
            height: 3rem !important;
            font-size: 1.1rem !important;
        }
        
        /* 文字輸入框優化 */
        .stTextInput > div > div > input {
            height: 3rem !important;
            font-size: 1.1rem !important;
            padding: 0.75rem !important;
        }
        
        /* 檔案上傳器優化 */
        .stFileUploader {
            margin: 1rem 0 !important;
        }
        
        .stFileUploader > div {
            border: 2px dashed #ccc !important;
            border-radius: 8px !important;
            padding: 2rem !important;
            text-align: center !important;
        }
        
        /* 滑桿優化 */
        .stSlider {
            margin: 1rem 0 !important;
        }
        
        /* 表格響應式 */
        .stDataFrame {
            font-size: 0.9rem !important;
        }
        
        /* 展開器優化 */
        .streamlit-expanderHeader {
            font-size: 1.1rem !important;
            padding: 1rem !important;
        }
        
        /* 標籤頁優化 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 3rem !important;
            padding: 0.5rem 1rem !important;
            font-size: 1rem !important;
        }
    }
    
    /* 移動端專用卡片設計 */
    .mobile-feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 20px rgba(31, 38, 135, 0.3);
        transition: transform 0.2s ease;
        text-align: center;
    }
    
    .mobile-feature-card:active {
        transform: scale(0.98);
    }
    
    @media (max-width: 768px) {
        .mobile-feature-card {
            padding: 1.2rem;
            margin: 0.8rem 0;
            border-radius: 10px;
        }
        
        .mobile-feature-card h3 {
            font-size: 1.4rem !important;
            margin-bottom: 0.8rem !important;
        }
        
        .mobile-feature-card p {
            font-size: 1rem !important;
            line-height: 1.4 !important;
        }
    }
    
    /* 移動端狀態指示器 */
    .mobile-status {
        display: inline-flex;
        align-items: center;
        background: #28a745;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 1rem;
        margin: 0.5rem;
        font-weight: bold;
    }
    
    /* 移動端工具欄 */
    .mobile-toolbar {
        position: sticky;
        top: 0;
        background: white;
        padding: 0.5rem;
        border-bottom: 1px solid #eee;
        z-index: 100;
        text-align: center;
    }
    
    /* 手勢友好的間距 */
    @media (max-width: 768px) {
        .element-container {
            margin-bottom: 1rem !important;
        }
        
        .stMarkdown {
            margin: 0.5rem 0 !important;
        }
        
        /* 觸控目標最小44px */
        button, .stSelectbox, .stTextInput, .stFileUploader {
            min-height: 44px !important;
        }
    }
    
    /* 隱藏Streamlit標記 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 移動端導航優化 */
    @media (max-width: 768px) {
        .css-1v0mbdj {
            font-size: 1.1rem !important;
            padding: 0.75rem !important;
        }
        
        .css-1v0mbdj .css-1vq4p4l {
            font-size: 1.1rem !important;
            padding: 0.5rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def show_header(title, subtitle=None):
    """顯示頁面標題"""
    st.markdown(f"""
    <div class="main-header">
        <h1>{title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def show_footer():
    """顯示頁面頁腳"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <p>📄 智能文件處理系統 v1.0.0</p>
            <p>🕒 最後更新時間: {current_time}</p>
            <p>💡 由智慧文件處理團隊開發</p>
        </div>
        """, unsafe_allow_html=True)

def show_feature_card(title, content, icon="📋"):
    """顯示功能卡片"""
    st.markdown(f"""
    <div class="feature-card">
        <h3>{icon} {title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def show_success_message(message):
    """顯示成功訊息"""
    st.markdown(f"""
    <div class="success-message">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)

def show_warning_message(message):
    """顯示警告訊息"""
    st.markdown(f"""
    <div class="warning-message">
        ⚠️ {message}
    </div>
    """, unsafe_allow_html=True)

def show_error_message(message):
    """顯示錯誤訊息"""
    st.markdown(f"""
    <div style="background-color: #f8d7da; color: #721c24; padding: 1rem; border-radius: 5px; border: 1px solid #f5c6cb; margin: 1rem 0;">
        ❌ {message}
    </div>
    """, unsafe_allow_html=True)

def show_info_box(title, content):
    """顯示資訊框"""
    with st.expander(f"ℹ️ {title}"):
        st.write(content)

def create_two_columns():
    """建立兩欄布局"""
    return st.columns(2)

def create_three_columns():
    """建立三欄布局"""
    return st.columns(3)

def show_divider():
    """顯示分隔線"""
    st.markdown("---")

def show_loading_spinner(text="處理中..."):
    """顯示載入動畫"""
    return st.spinner(text)
```

---

## 📁 檔案2：`pages/home_page.py`

**步驟：**
1. 點擊倉庫中的 `pages/home_page.py`
2. 點擊 ✏️ 編輯按鈕
3. 選擇所有內容並刪除
4. 複製下方內容並貼上
5. 提交：`Update mobile home page layout`

**檔案內容：**
```python
# 檔名: pages/home_page.py
# 系統首頁

import streamlit as st
from datetime import datetime

def show_home_page():
    """顯示系統首頁"""
    
    # 移動端優化的標題
    st.markdown("""
    <div class="mobile-toolbar">
        <h1>📄 PDF文件比對系統</h1>
        <div class="mobile-status">✅ 系統正常運行</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 手機優化的功能卡片
    st.markdown("## 🎯 主要功能")
    
    # 移動端友好的垂直卡片布局
    st.markdown("""
    <div class="mobile-feature-card">
        <h3>🎨 PDF 變數標記</h3>
        <p>📤 上傳PDF範本 → ✏️ 標記變數位置 → 💾 建立範本庫</p>
        <p><strong>快速開始：</strong>上傳您的第一個PDF範本</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="mobile-feature-card">
        <h3>📝 檔案輸入與生成</h3>
        <p>✏️ 填入變數值 → 🔄 自動生成 → 📋 下載文件</p>
        <p><strong>快速開始：</strong>選擇範本填寫資料</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="mobile-feature-card">
        <h3>🔍 文件比對檢查</h3>
        <p>📊 上傳文件 → 🎯 智慧比對 → 📋 生成報告</p>
        <p><strong>快速開始：</strong>上傳需要檢查的文件</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="mobile-feature-card">
        <h3>⚙️ 範本管理設定</h3>
        <p>📂 管理範本 → 🏷️ 分類整理 → 📊 查看統計</p>
        <p><strong>快速開始：</strong>檢視您的範本庫</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 簡化的工作流程
    st.markdown("## 🔄 簡單三步驟")
    
    st.markdown("""
    <div class="mobile-feature-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <div style='text-align: center;'>
            <h3>📱 超簡單操作流程</h3>
            <br>
            <div style='font-size: 1.5rem; margin: 1rem 0;'>
                1️⃣ <strong>上傳範本</strong> → 標記變數
            </div>
            <div style='font-size: 1.5rem; margin: 1rem 0;'>
                2️⃣ <strong>填寫資料</strong> → 生成文件  
            </div>
            <div style='font-size: 1.5rem; margin: 1rem 0;'>
                3️⃣ <strong>比對檢查</strong> → 下載報告
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 手機優化的快速開始按鈕
    st.markdown("## 🚀 立即開始")
    
    # 大按鈕垂直排列，適合手機點擊
    if st.button("🎨 開始標記PDF範本", use_container_width=True, type="primary"):
        st.session_state['page_selection'] = '🎨 PDF 變數標記'
        st.rerun()
    
    if st.button("📝 輸入資料生成文件", use_container_width=True):
        st.session_state['page_selection'] = '📝 檔案輸入與生成'
        st.rerun()
    
    if st.button("🔍 文件比對檢查", use_container_width=True):
        st.session_state['page_selection'] = '🔍 文件比對檢查'
        st.rerun()
    
    # 簡化的系統狀態
    st.markdown("---")
    st.markdown("## 📊 系統狀態")
    
    # 手機友好的雙欄布局
    col1, col2 = st.columns(2)
    
    with col1:
        # 模擬資料
        template_count = 0
        try:
            from core.pdf_annotation_system import PDFAnnotationSystem
            system = PDFAnnotationSystem()
            templates = system.get_templates_list()
            template_count = len(templates) if templates else 0
        except:
            pass
        st.metric("📄 範本數量", template_count)
    
    with col2:
        st.metric("✅ 系統狀態", "正常運行")
    
    # 簡化的使用提示
    st.markdown("## 💡 使用提示")
    
    st.info("""
    **📱 行動裝置最佳化**
    - 支援手機和平板瀏覽
    - 觸控操作友好設計
    - 自動儲存工作進度
    """)
    
    # 技術資訊收合
    with st.expander("🔧 技術資訊"):
        st.markdown("""
        **系統版本：** v3.0 (行動優化版)  
        **支援格式：** PDF文件  
        **瀏覽器：** Chrome, Firefox, Safari  
        **架構：** Streamlit + SQLite
        """)

if __name__ == "__main__":
    show_home_page()
```

---

## ⏰ 完成後

1. ✅ 兩個檔案都上傳完成
2. ⏳ 等待 3-5 分鐘讓 Streamlit Cloud 重新部署
3. 📱 用手機打開測試：https://bei-da-pdf-comparison.streamlit.app

**準備好了嗎？開始上傳吧！** 🚀