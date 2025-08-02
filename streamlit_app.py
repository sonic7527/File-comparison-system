import streamlit as st
import os

# --- 強制禁用所有可能導致權限問題的功能 ---
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
os.environ['STREAMLIT_GLOBAL_DEVELOPMENT_MODE'] = 'false'
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'

# --- 頁面配置 ---
st.set_page_config(
    page_title="北大文件比對與範本管理系統",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 全局樣式 ---
st.markdown("""
    <style>
        header, footer { display: none !important; }
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

# --- 主頁面 ---
def show_home_page():
    st.markdown('<div class="title-container"><h1>北大文件比對與範本管理系統</h1><p>一個專業、高效的文件自動化解決方案</p></div>', unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        st.markdown('<div class="feature-card"><div class="icon">🚀</div><h3>檔案輸入與生成</h3><p>根據範本輸入參數<br>快速生成標準化文件</p></div>', unsafe_allow_html=True)
        if st.button("前往生成", key="nav_gen", use_container_width=True):
            st.session_state.current_page = "📝 智能文件生成與管理"
            st.rerun()
    with cols[1]:
        st.markdown('<div class="feature-card"><div class="icon">⚙️</div><h3>範本管理設定</h3><p>集中管理範本群組<br>有效組織與重複利用</p></div>', unsafe_allow_html=True)
        if st.button("前往管理", key="nav_mgmt", use_container_width=True):
            st.session_state.current_page = "📝 智能文件生成與管理"
            st.rerun()
    with cols[2]:
        st.markdown('<div class="feature-card"><div class="icon">🔍</div><h3>文件比對檢查</h3><p>多範本智慧比對<br>自動生成差異清單</p></div>', unsafe_allow_html=True)
        if st.button("前往比對", key="nav_comp", use_container_width=True):
            st.session_state.current_page = "🔍 文件比對"
            st.rerun()

    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    stat_cols = st.columns(3)
    stat_cols[0].metric(label="📊 總範本群組數", value=3)
    stat_cols[1].metric(label="📂 總範本檔案數", value=12)
    stat_cols[2].metric(label="📈 今日已生成文件", value=15)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 文件生成頁面 ---
def show_document_generator():
    st.title("📝 智能文件生成與管理")
    st.info("此功能正在開發中，敬請期待！")
    
    uploaded_file = st.file_uploader("上傳 Excel 文件", type=['xlsx', 'xls'])
    if uploaded_file is not None:
        st.success(f"已上傳文件: {uploaded_file.name}")
        st.write("文件處理功能正在開發中...")

# --- 文件比對頁面 ---
def show_comparison_page():
    st.title("🔍 文件比對系統")
    st.info("此功能正在開發中，敬請期待！")
    
    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("上傳第一個文件", type=['pdf', 'docx', 'xlsx'])
    with col2:
        file2 = st.file_uploader("上傳第二個文件", type=['pdf', 'docx', 'xlsx'])
    
    if file1 and file2:
        st.success("文件比對功能正在開發中...")

# --- 主程式 ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 系統首頁"

# 側邊欄導航
st.sidebar.title("📋 功能選單")

page_options = ["🏠 系統首頁", "📝 智能文件生成與管理", "🔍 文件比對"]

selected_page = st.sidebar.selectbox(
    "選擇功能", 
    page_options, 
    index=page_options.index(st.session_state.current_page),
    key="sidebar_nav"
)

if selected_page != st.session_state.current_page:
    st.session_state.current_page = selected_page
    st.rerun()

# 根據選擇的頁面顯示內容
if st.session_state.current_page == "🏠 系統首頁":
    show_home_page()
elif st.session_state.current_page == "📝 智能文件生成與管理":
    show_document_generator()
elif st.session_state.current_page == "🔍 文件比對":
    show_comparison_page() 