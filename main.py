import streamlit as st
import os
import sqlite3

# --- 核心模組導入 (路徑已更新) ---
from core.database import init_database, DB_PATH
from views.document_generator import show_document_generator
from views.document_comparison import show_document_comparison_main
from utils.storage_monitor import get_storage_stats

# --- 頁面配置 ---
st.set_page_config(
    page_title="北大文件比對與範本管理系統",
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

# --- 全局樣式 (已清理) ---
def apply_global_styles():
    st.markdown("""
        <style>
            /* 移除了隱藏 stSidebarNav 的 CSS，因為結構性問題已解決 */
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
                min-height: 280px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                align-items: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            .feature-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 0 25px rgba(0, 191, 255, 0.5);
            }
            .feature-card .icon { 
                font-size: 3.5rem; 
                margin-bottom: 1.5rem; 
                filter: drop-shadow(0 0 5px rgba(0, 191, 255, 0.7));
            }
            .feature-card h3 { color: #ffffff; font-weight: 600; margin-bottom: 1rem; }
            .feature-card p { color: #a9b4c2; font-size: 0.95rem; margin-bottom: 2rem; }
            .feature-card .stButton > button {
                background: linear-gradient(135deg, #00bfff 0%, #0080ff 100%);
                border: none;
                border-radius: 15px;
                padding: 12px 30px;
                color: white;
                font-weight: 600;
                font-size: 1rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0, 191, 255, 0.3);
                width: 100%;
                margin-top: auto;
            }
            .feature-card .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 191, 255, 0.4);
                background: linear-gradient(135deg, #00a6e6 0%, #0066cc 100%);
            }
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
            .storage-warning {
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                border-left: 4px solid;
            }
            .storage-warning.danger { background: rgba(220, 53, 69, 0.2); border-left-color: #dc3545; }
            .storage-warning.warning { background: rgba(255, 193, 7, 0.2); border-left-color: #ffc107; }
            .storage-warning.info { background: rgba(13, 202, 240, 0.2); border-left-color: #0dcaf0; }
            .storage-warning.success { background: rgba(25, 135, 84, 0.2); border-left-color: #198754; }
            .storage-progress {
                background: rgba(27, 38, 59, 0.6);
                border-radius: 10px;
                padding: 1rem;
                margin: 1rem 0;
            }
            .progress-bar {
                background: linear-gradient(90deg, #00bfff 0%, #0080ff 100%);
                height: 8px;
                border-radius: 4px;
                transition: width 0.3s ease;
            }
            .back-button {
                background: rgba(27, 38, 59, 0.8);
                border: 1px solid rgba(129, 153, 189, 0.3);
                border-radius: 10px;
                padding: 8px 16px;
                color: #a9b4c2;
                font-size: 0.9rem;
                transition: all 0.3s ease;
                margin-bottom: 1rem;
            }
            .back-button:hover {
                background: rgba(27, 38, 59, 1);
                color: #ffffff;
                border-color: rgba(0, 191, 255, 0.5);
            }
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
    st.markdown('<div class="title-container"><h1>北大文件比對與範本管理系統</h1><p>一個專業、高效的文件自動化解決方案</p></div>', unsafe_allow_html=True)

    # 主要功能卡片
    cols = st.columns(3)
    with cols[0]:
        st.markdown('<div class="feature-card"><div class="icon">🚀</div><h3>檔案輸入與生成</h3><p>根據範本輸入參數<br>快速生成標準化文件</p></div>', unsafe_allow_html=True)
        if st.button("前往生成", key="nav_gen", use_container_width=True, help="進入文件生成功能"):
            navigate_to("📝 智能文件生成與管理")
    
    with cols[1]:
        st.markdown('<div class="feature-card"><div class="icon">⚙️</div><h3>範本管理設定</h3><p>集中管理範本群組<br>有效組織與重複利用</p></div>', unsafe_allow_html=True)
        if st.button("前往管理", key="nav_mgmt", use_container_width=True, help="進入範本管理功能"):
            navigate_to("📝 智能文件生成與管理")
    
    with cols[2]:
        st.markdown('<div class="feature-card"><div class="icon">🔍</div><h3>文件比對檢查</h3><p>多範本智慧比對<br>自動生成差異清單</p></div>', unsafe_allow_html=True)
        if st.button("前往比對", key="nav_comp", use_container_width=True, help="進入文件比對功能"):
            navigate_to("🔍 文件比對")

    # 系統統計
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    total_groups, total_files, generated_today = get_system_stats()
    stat_cols = st.columns(3)
    stat_cols[0].metric(label="📊 總範本群組數", value=total_groups)
    stat_cols[1].metric(label="📂 總範本檔案數", value=total_files)
    stat_cols[2].metric(label="📈 今日已生成文件 (模擬)", value=generated_today)
    st.markdown('</div>', unsafe_allow_html=True)

    # 容量監控區域（移到最下方）
    st.markdown("---")
    st.subheader("💾 系統容量監控")
    
    try:
        storage_stats = get_storage_stats()
        
        # 容量警告
        warning_class = storage_stats['warning_level']
        st.markdown(f'<div class="storage-warning {warning_class}">{storage_stats["warning_message"]}</div>', unsafe_allow_html=True)
        
        # 容量進度條
        st.markdown('<div class="storage-progress">', unsafe_allow_html=True)
        st.markdown(f'<h4>💾 儲存空間使用量：{storage_stats["formatted_size"]} ({storage_stats["usage_percentage"]}%)</h4>', unsafe_allow_html=True)
        st.progress(storage_stats['usage_percentage'] / 100)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 範本容量統計
        if 'template_usage' in storage_stats and storage_stats['template_usage']:
            template_usage = storage_stats['template_usage']
            st.markdown("---")
            st.subheader("📊 範本容量統計")
            
            col1, col2 = st.columns(2)
            with col1:
                if "智能生成範本" in template_usage:
                    gen_usage = template_usage["智能生成範本"]
                    st.metric(
                        "🚀 智能生成範本", 
                        f"{gen_usage['size_mb']} MB", 
                        f"{gen_usage['file_count']} 個檔案"
                    )
            
            with col2:
                if "比對範本" in template_usage:
                    comp_usage = template_usage["比對範本"]
                    st.metric(
                        "🔍 比對範本", 
                        f"{comp_usage['size_mb']} MB", 
                        f"{comp_usage['file_count']} 個檔案"
                    )
            
            st.info("💡 **提示**：範本容量管理請前往各功能頁面的範本管理區域")
                    
    except Exception as e:
        st.warning("容量監控暫時無法載入，請稍後再試")

def show_comparison_page():
    show_document_comparison_main()

# --- 主程式 (邏輯已更新) ---
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
        show_document_generator()
    elif st.session_state.page_selection == "🔍 文件比對":
        show_comparison_page()

if __name__ == "__main__":
    main()

# 強制更新觸發器 3
