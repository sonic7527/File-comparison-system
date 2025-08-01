import streamlit as st
import os
import sqlite3

# 移除 sys.path 操作，讓 Streamlit 以標準方式處理路徑
from core.database import init_database, DB_PATH

# --- 頁面配置 ---
st.set_page_config(
    page_title="文件比對與範本管理系統",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 資料庫查詢 (用於統計) ---
def get_system_stats():
    """從資料庫獲取系統統計數據"""
    try:
        if not os.path.exists(os.path.dirname(DB_PATH)):
            os.makedirs(os.path.dirname(DB_PATH))
        
        init_database()
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM template_groups")
            total_groups = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM template_files")
            total_files = cursor.fetchone()[0]
            generated_today = 15 
            return total_groups, total_files, generated_today
    except Exception:
        return 0, 0, 0

# --- 全局樣式 ---
def apply_global_styles():
    st.markdown("""
        <style>
            div[data-testid="stSidebarNav"], header, footer { display: none !important; }
            .main {
                background: linear-gradient(135deg, #0d1b2a 0%, #000000 100%);
                color: #e0e1dd;
            }
            .main .block-container { padding: 2rem; }
            [data-testid="stSidebar"] {
                background: #0d1b2a;
                border-right: 1px solid #1b263b;
            }
            .title-container { text-align: center; margin-bottom: 3rem; }
            .title-container h1 { font-weight: 700; color: #ffffff; letter-spacing: 2px; }
            .title-container p { color: #778da9; font-size: 1.2rem; }
            .feature-card {
                background: rgba(27, 38, 59, 0.6);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 2rem;
                text-align: center;
                border: 1px solid rgba(129, 153, 189, 0.2);
                min-height: 230px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .feature-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 0 25px rgba(0, 191, 255, 0.5);
            }
            .feature-card .icon { font-size: 3.5rem; margin-bottom: 1.5rem; filter: drop-shadow(0 0 5px rgba(0, 191, 255, 0.7));}
            .feature-card h3 { color: #ffffff; font-weight: 600; }
            .feature-card p { color: #a9b4c2; font-size: 0.95rem; }
            .stats-container {
                margin-top: 3rem;
                padding: 2rem;
                background: rgba(27, 38, 59, 0.4);
                border-radius: 20px;
                border: 1px solid rgba(129, 153, 189, 0.2);
            }
            [data-testid="stMetric"] { background-color: transparent; border-radius: 10px; padding: 1rem; text-align: center; }
            [data-testid="stMetricLabel"] { color: #778da9; font-weight: 500; }
            [data-testid="stMetricValue"] { color: #ffffff; font-size: 2.5rem; font-weight: 700; }
        </style>
    """, unsafe_allow_html=True)

# --- 初始化 ---
def initialize_app():
    init_database()
    if 'page_selection' not in st.session_state:
        st.session_state.page_selection = "🏠 系統首頁"

# --- 頁面跳轉函數 ---
def navigate_to(page_name):
    st.session_state.page_selection = page_name
    st.rerun()

# --- 頁面渲染 ---
def show_home_page():
    st.markdown('<div class="title-container"><h1>文件比對與範本管理系統</h1><p>一個專業、高效的文件自動化解決方案</p></div>', unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        st.markdown('<div class="feature-card"><div class="icon">🚀</div><h3>檔案輸入與生成</h3><p>根據範本輸入參數<br>快速生成標準化文件</p></div>', unsafe_allow_html=True)
        if st.button("前往生成", key="nav_gen", use_container_width=True):
            navigate_to("📝 智能文件生成與管理")
    with cols[1]:
        st.markdown('<div class="feature-card"><div class="icon">⚙️</div><h3>範本管理設定</h3><p>集中管理範本群組<br>有效組織與重複利用</p></div>', unsafe_allow_html=True)
        if st.button("前往管理", key="nav_mgmt", use_container_width=True):
            navigate_to("📝 智能文件生成與管理")
    with cols[2]:
        st.markdown('<div class="feature-card"><div class="icon">🔍</div><h3>文件比對檢查</h3><p>多範本智慧比對<br>自動生成差異清單</p></div>', unsafe_allow_html=True)
        if st.button("前往比對", key="nav_comp", use_container_width=True):
            navigate_to("🔍 文件比對")

    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    total_groups, total_files, generated_today = get_system_stats()
    stat_cols = st.columns(3)
    stat_cols[0].metric(label="📊 總範本群組數", value=total_groups)
    stat_cols[1].metric(label="📂 總範本檔案數", value=total_files)
    stat_cols[2].metric(label="📈 今日已生成文件 (模擬)", value=generated_today)
    st.markdown('</div>', unsafe_allow_html=True)

def show_comparison_page():
    st.title("🔍 文件比對系統")
    st.info("此功能正在開發中，敬請期待！")

# --- 主程式 ---
def main():
    apply_global_styles()
    initialize_app()
    
    page_options = ["🏠 系統首頁", "📝 智能文件生成與管理", "🔍 文件比對"]
    try:
        current_index = page_options.index(st.session_state.page_selection)
    except ValueError:
        current_index = 0

    st.sidebar.title("📋 功能選單")
    st.session_state.page_selection = st.sidebar.selectbox(
        "選擇功能", 
        page_options, 
        index=current_index,
        key="main_page_selector"
    )
    
    if st.session_state.page_selection == "🏠 系統首頁":
        show_home_page()
    elif st.session_state.page_selection == "📝 智能文件生成與管理":
        from pages.document_generator import show_document_generator
        show_document_generator()
    elif st.session_state.page_selection == "🔍 文件比對":
        show_comparison_page()

if __name__ == "__main__":
    main()
