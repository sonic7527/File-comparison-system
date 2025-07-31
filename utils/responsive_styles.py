"""響應式設計樣式"""
import streamlit as st


def apply_responsive_styles():
    """應用響應式設計樣式"""
    st.markdown("""
    <style>
    /* 基礎響應式設計 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1200px;
    }
    
    /* 手機端優化 */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
            padding-top: 0.5rem;
        }
        
        /* 側邊欄優化 */
        .css-1d391kg {
            width: 280px;
        }
        
        /* 標題字體大小調整 */
        h1 {
            font-size: 1.8rem !important;
            line-height: 1.2 !important;
        }
        
        h2 {
            font-size: 1.4rem !important;
            line-height: 1.3 !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
            line-height: 1.3 !important;
        }
        
        /* 按鈕優化 */
        .stButton > button {
            width: 100% !important;
            margin: 0.25rem 0 !important;
            padding: 0.5rem 1rem !important;
            font-size: 0.9rem !important;
        }
        
        /* 選擇框優化 */
        .stSelectbox > div > div {
            width: 100% !important;
        }
        
        /* 檔案上傳器優化 */
        .stFileUploader > div {
            width: 100% !important;
        }
    }
    
    /* 平板端優化 */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            max-width: 90%;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    
    /* 卡片設計 */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.5);
    }
    
    @media (max-width: 768px) {
        .feature-card {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
        }
    }
    
    /* 狀態卡片 */
    .status-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #FF6B6B;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* 側邊欄美化 */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: white;
    }
    
    /* 指標卡片 */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* 進度條優化 */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
    }
    
    /* 表格響應式 */
    .dataframe {
        width: 100% !important;
    }
    
    @media (max-width: 768px) {
        .dataframe {
            font-size: 0.8rem !important;
        }
    }
    
    /* 圖片響應式 */
    .stImage > img {
        max-width: 100% !important;
        height: auto !important;
    }
    
    /* 容器間距優化 */
    .element-container {
        margin-bottom: 1rem;
    }
    
    @media (max-width: 768px) {
        .element-container {
            margin-bottom: 0.5rem;
        }
    }
    
    /* 載入動畫 */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
    }
    
    .spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #FF6B6B;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* 警告和成功訊息 */
    .stAlert {
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* 隱藏Streamlit標記 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 深色模式支援 */
    @media (prefers-color-scheme: dark) {
        .feature-card {
            background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        }
        
        .status-card {
            background: #2d3748;
            color: white;
        }
        
        .metric-card {
            background: #2d3748;
            color: white;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def create_responsive_columns(mobile_cols=1, tablet_cols=2, desktop_cols=3):
    """創建響應式列布局"""
    # 檢測螢幕寬度 (簡化版)
    return st.columns(desktop_cols)


def mobile_friendly_sidebar():
    """移動端友好的側邊欄"""
    with st.sidebar:
        st.markdown("""
        <style>
        .sidebar-content {
            padding: 0.5rem;
        }
        
        @media (max-width: 768px) {
            .sidebar-content {
                font-size: 0.9rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)


def responsive_container(content_func, padding=True):
    """響應式容器包裝器"""
    container_class = "responsive-container"
    if padding:
        container_class += " with-padding"
    
    with st.container():
        st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
        content_func()
        st.markdown('</div>', unsafe_allow_html=True)


def show_mobile_warning():
    """在小屏幕上顯示友好提醒"""
    st.markdown("""
    <div style="display: none;" id="mobile-warning">
    <div style="background: #FF6B6B; color: white; padding: 0.5rem; border-radius: 5px; text-align: center; margin-bottom: 1rem;">
        📱 您正在使用移動設備瀏覽。建議橫屏查看以獲得更好體驗。
    </div>
    </div>
    
    <script>
    if (window.innerWidth <= 768) {
        document.getElementById('mobile-warning').style.display = 'block';
    }
    </script>
    """, unsafe_allow_html=True)