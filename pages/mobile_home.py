# 檔名: pages/mobile_home.py
# 功能: 手機版專用介面

import streamlit as st
from datetime import datetime

def apply_mobile_css():
    """專為手機版設計的CSS樣式"""
    st.markdown("""
        <style>
            /* --- 全局樣式 --- */
            .stApp {
                background-color: #F0F2F5; /* iOS淺灰色背景 */
            }
            .main .block-container {
                padding: 1rem;
            }

            /* --- iOS 風格卡片 --- */
            .ios-card {
                background-color: white;
                border-radius: 12px;
                padding: 18px;
                margin-bottom: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                border: 1px solid #E5E5E5;
            }
            .ios-card h2, .ios-card h3 {
                color: #1C1C1E;
                margin-top: 0;
                padding-bottom: 5px;
                border-bottom: 1px solid #E5E5E5;
            }

            /* --- 按鈕樣式 --- */
            .stButton>button {
                border-radius: 10px;
                font-weight: 600;
                color: #007AFF; /* iOS藍色 */
                background-color: #EFEFF4;
                border: none;
                padding: 10px 15px;
            }
            .stButton>button:hover {
                background-color: #DCDCE0;
            }
            
            /* --- 返回按鈕 --- */
            .back-button {
                text-align: left;
                margin-bottom: 15px;
            }

        </style>
    """, unsafe_allow_html=True)

def mobile_home_page():
    """手機版主頁"""
    st.html("""
        <div class="ios-card">
            <h2>📱 功能選單</h2>
        </div>
    """)

    # 功能按鈕
    if st.button("📄 智能文件生成", use_container_width=True):
        st.session_state['mobile_page'] = 'document_generator'
        st.experimental_rerun()
    
    if st.button("🔍 文件比對檢查", use_container_width=True):
        st.session_state['mobile_page'] = 'document_comparison'
        st.experimental_rerun()
        
    st.markdown("---")
    if st.button("💻 切換回電腦版", use_container_width=True):
        st.session_state['mobile_mode'] = False
        st.session_state.pop('mobile_page', None) # 清理手機頁面狀態
        st.experimental_rerun()

def mobile_main():
    """手機版主應用程式進入點"""
    apply_mobile_css()

    # 頁面路由器
    page = st.session_state.get('mobile_page', 'home')

    if page != 'home':
        # 顯示返回按鈕
        st.html('<div class="back-button"><button onclick="window.history.back()">← 返回</button></div>')


    if page == 'home':
        mobile_home_page()
    elif page == 'document_generator':
        from .document_generator import document_generator_tab
        st.html('<div class="ios-card"><h2>📄 智能文件生成</h2></div>')
        document_generator_tab()
    elif page == 'document_comparison':
        from .document_comparison import document_comparison_page
        st.html('<div class="ios-card"><h2>🔍 文件比對檢查</h2></div>')
        document_comparison_page()

    # 頁腳
    st.markdown(
        f"""
        <div style='text-align: center; color: #888; padding: 2rem 1rem 1rem 1rem; font-size: 0.8rem;'>
            系統版本 v3.0 | {datetime.now().strftime("%Y-%m-%d")}
        </div>
        """,
        unsafe_allow_html=True
    )
