"""UI 組件模組 - 響應式設計版本"""
import streamlit as st
from datetime import datetime

def apply_custom_css():
    """智能設備檢測與響應式CSS樣式"""
    st.markdown("""
    <script>
    // 設備檢測JavaScript
    function detectDevice() {
        const userAgent = navigator.userAgent;
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
        const isTablet = /iPad|Android(?=.*\\bMobile\\b)/i.test(userAgent);
        
        // 添加設備類型到body
        if (isMobile && !isTablet) {
            document.body.classList.add('mobile-device');
        } else if (isTablet) {
            document.body.classList.add('tablet-device');
        } else {
            document.body.classList.add('desktop-device');
        }
    }
    
    // 頁面載入後執行
    document.addEventListener('DOMContentLoaded', detectDevice);
    
    // 對於Streamlit的動態載入
    setTimeout(detectDevice, 100);
    </script>
    
    <style>
    /* 預設為電腦版樣式 */
    .main .block-container {
        padding: 1rem 2rem;
        max-width: none;
    }
    
    /* 電腦版專用樣式 */
    .desktop-device .main .block-container {
        padding: 2rem 3rem;
        max-width: none;
    }
    
    /* 手機端專用樣式 */
    .mobile-device .main .block-container {
        padding: 0.3rem !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    
    .mobile-device h1 { 
        font-size: 1.8rem !important; 
        line-height: 1.2 !important; 
        margin-bottom: 1rem !important;
        text-align: center !important;
    }
    
    .mobile-device h2 { 
        font-size: 1.6rem !important; 
        line-height: 1.2 !important; 
        margin: 1rem 0 !important;
    }
    
    .mobile-device h3 { 
        font-size: 1.3rem !important; 
        line-height: 1.3 !important; 
        margin: 0.8rem 0 !important;
    }
    
    .mobile-device .stButton > button {
        width: 100% !important;
        height: 3.5rem !important;
        margin: 0.5rem 0 !important;
        padding: 1rem !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    
    /* 手機版：將橫向布局改為縱向 */
    .mobile-device .stColumns {
        flex-direction: column !important;
    }
    
    .mobile-device .stColumns > div {
        width: 100% !important;
        margin-bottom: 1rem !important;
    }
    
    /* 手機版：將工作流程改為垂直 */
    .mobile-device div[style*="display: flex"] {
        flex-direction: column !important;
        text-align: center !important;
    }
    
    .mobile-device div[style*="display: flex"] > div {
        margin: 0.5rem 0 !important;
    }
    
    /* 平板端樣式 */
    .tablet-device .main .block-container {
        padding: 1rem 1.5rem !important;
        max-width: 95% !important;
    }
    
    /* 電腦版保持原始樣式 */
    .desktop-device h1 {
        font-size: 2.5rem !important;
        line-height: 1.2 !important;
        margin-bottom: 1.5rem !important;
    }
    
    .desktop-device .stButton > button {
        height: auto !important;
        padding: 0.5rem 1rem !important;
        font-size: 1rem !important;
        border-radius: 4px !important;
    }
    
    /* 後備的媒體查詢（如果JavaScript失敗） */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.3rem !important;
            margin: 0 !important;
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
