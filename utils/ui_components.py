# 檔名: utils/ui_components.py
# 用於存放可重用的UI組件和樣式

import streamlit as st
import os
import base64

def apply_custom_css():
    """載入並應用所有自定義CSS文件"""
    
    # --- 核心CSS ---
    core_css = """
    <style>
    /* 隱藏 Streamlit 的預設選單和頁腳 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}

    /* 隱藏 Streamlit 自動生成的側邊欄導航 (我們會用自訂的) */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* 統一卡片樣式 */
    .feature-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .feature-card h3 {
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    .feature-card ul {
        list-style: none;
        padding-left: 0;
    }
    
    .feature-card li {
        padding: 0.3rem 0;
        color: #34495e;
        font-weight: 500;
    }
    </style>
    """
    st.markdown(core_css, unsafe_allow_html=True)

    # --- 載入手機版專用CSS ---
    try:
        css_path = os.path.join(os.path.dirname(__file__), "mobile_styles.css")
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("`mobile_styles.css` not found. Mobile view might not be optimized.")

def mobile_navigation_bar():
    """
    在頁面底部顯示一個手機專用的固定導航列。
    使用 Streamlit 按鈕和 session_state 來處理頁面切換，以避免重新載入。
    """
    # 檢查是否在 session_state 中有當前頁面，若無則預設為首頁
    if 'page_selection' not in st.session_state:
        st.session_state['page_selection'] = "🏠 系統首頁"

    current_page = st.session_state['page_selection']

    # 頁面選項和對應的圖示
    PAGES = {
        "🏠 系統首頁": "🏠",
        "🎨 PDF 變數標記": "🎨",
        "📝 檔案輸入與生成": "📝",
        "🔍 文件比對檢查": "🔍",
        "⚙️ 範本管理設定": "⚙️",
    }
    
    # 將導航列固定在頁面底部
    st.markdown('<div class="mobile-nav">', unsafe_allow_html=True)
    
    # 使用 st.columns 創建等寬的按鈕佈局
    cols = st.columns(len(PAGES))
    for i, (page_name, icon) in enumerate(PAGES.items()):
        with cols[i]:
            # 檢查當前頁面以應用 'active' 樣式
            active_class = "active" if current_page == page_name else ""
            
            # 使用 st.markdown 來創建可點擊的按鈕，並注入 HTML/CSS class
            st.markdown(
                f"""
                <button class="mobile-nav-button {active_class}" onclick="
                    // 使用 Streamlit 的 setComponentValue 來觸發Python回調
                    window.parent.document.querySelector('[data-testid=\"stFormSubmitButton\"]').click();
                ">
                    <div class="icon">{icon}</div>
                    <div>{page_name.split(' ')[1]}</div>
                </button>
                """,
                unsafe_allow_html=True
            )
            # 實際的頁面切換邏輯
            if st.button(f"nav_{page_name}", key=f"nav_btn_{i}", help=page_name):
                 st.session_state['page_selection'] = page_name
                 st.experimental_rerun()


    st.markdown('</div>', unsafe_allow_html=True)

    # 隱藏 Streamlit button chrome
    st.markdown("""
        <style>
            /* Hack to hide the streamlit buttons used for callbacks */
            div[data-testid="stForm"] {
                position: fixed;
                bottom: -100px;
            }
        </style>
    """, unsafe_allow_html=True)


def mobile_page_switch():
    """
    一個隱藏的表單，用於接收來自底部導航列JS點擊的回調。
    """
    with st.form("mobile_nav_form"):
        submitted = st.form_submit_button("Submit", help="Internal use for mobile navigation")
        if submitted:
            # 這裡的邏輯由JS觸發，並由每個按鈕的 st.button 處理
            pass
