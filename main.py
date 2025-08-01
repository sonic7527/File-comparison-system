import streamlit as st
import sys
import os

# --- 路徑與初始化 ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.database import init_database

# --- 頁面配置 ---
st.set_page_config(
    page_title="📄 文件比對與範本管理系統",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 全局樣式 ---
def apply_global_styles():
    st.markdown("""
        <style>
            /* 徹底隱藏Streamlit頂部的多頁面導航選單 */
            div[data-testid="stSidebarNav"] {
                display: none !important;
            }
            /* 隱藏 Streamlit 預設 Header 和 Footer */
            header, footer {
                visibility: hidden;
            }
            .main .block-container {
                padding: 1rem 2rem 2rem 2rem;
            }
            /* 首頁樣式 */
            .title-container {
                text-align: center;
                margin: 1rem 0 2rem 0;
            }
            .title-container h1 { font-weight: 700; color: #2c3e50; }
            .title-container p { color: #576574; font-size: 1.1rem; }
            .feature-card {
                background: white;
                border-radius: 15px;
                padding: 2rem 1.5rem;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                border: 1px solid #e0e0e0;
                min-height: 220px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin-top: 1rem;
            }
            .feature-card .icon { font-size: 2.5rem; margin-bottom: 1rem; }
            .feature-card h3 { color: #34495e; font-weight: 600; margin-bottom: 0.5rem; }
            .feature-card p { color: #7f8c8d; font-size: 0.9rem; line-height: 1.4; }
        </style>
    """, unsafe_allow_html=True)

# --- 初始化 ---
def initialize_app():
    init_database()

# --- 頁面渲染 ---
def show_home_page():
    st.markdown("""
    <div class="title-container">
        <h1>📄 文件比對與範本管理系統</h1>
        <p>一個簡潔的、個人化的文件處理方案</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="feature-card"><div class="icon">🚀</div><h3>檔案輸入與生成</h3><p>根據範本輸入參數<br>生成標準化文件</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><div class="icon">⚙️</div><h3>範本管理設定</h3><p>範本群組管理<br>有效組織與重複利用</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card"><div class="icon">🔍</div><h3>文件比對檢查</h3><p>多範本智慧比對<br>自動生成差異清單</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="feature-card"><div class="icon">📄</div><h3>PDF 參數標記</h3><p>視覺化標定參數<br>建立可重複使用範本</p></div>', unsafe_allow_html=True)

def show_comparison_page():
    st.title("🔍 文件比對系統")
    st.info("此功能正在開發中，敬請期待！")

# --- 主程式 ---
def main():
    apply_global_styles()
    initialize_app()

    st.sidebar.title("📋 功能選單")
    page_selection = st.sidebar.selectbox(
        "選擇功能",
        ["🏠 系統首頁", "📝 智能文件生成與管理", "🔍 文件比對"],
        key="main_page_selector"
    )
    
    if page_selection == "🏠 系統首頁":
        show_home_page()
    elif page_selection == "📝 智能文件生成與管理":
        from pages.document_generator import show_document_generator
        show_document_generator()
    elif page_selection == "🔍 文件比對":
        show_comparison_page()

if __name__ == "__main__":
    main()