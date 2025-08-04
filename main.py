import streamlit as st
import os
import sqlite3

# --- 核心模組導入 (路徑已更新) ---
from core.database import init_database, DB_PATH
from views.document_generator import show_document_generator
from views.document_comparison import show_document_comparison_main
from utils.storage_monitor import get_storage_stats
from utils.ui_components import show_turso_status_card

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
            /* 防止側邊欄隱藏 */
            [data-testid="stSidebar"] {
                background: #0d1b2a !important;
                border-right: 1px solid #1b263b !important;
                min-width: 300px !important;
            }
            [data-testid="stSidebar"] [data-testid="stSidebarNav"] {
                display: block !important;
            }
            /* 狀態卡片樣式 - 固定在右上角 */
            .status-card {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                max-width: 350px;
                border-radius: 12px;
                padding: 16px 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
            }
            .status-card.success-dark {
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(51, 65, 85, 0.6) 100%);
                border-left: 4px solid #10b981;
                border: 1px solid rgba(16, 185, 129, 0.3);
                backdrop-filter: blur(15px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            .status-card.error-dark {
                background: linear-gradient(135deg, rgba(69, 10, 10, 0.6) 0%, rgba(127, 29, 29, 0.6) 100%);
                border-left: 4px solid #ef4444;
                border: 1px solid rgba(239, 68, 68, 0.3);
                backdrop-filter: blur(15px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            .status-card.warning-dark {
                background: linear-gradient(135deg, rgba(69, 26, 3, 0.6) 0%, rgba(120, 53, 15, 0.6) 100%);
                border-left: 4px solid #fbbf24;
                border: 1px solid rgba(251, 191, 36, 0.3);
                backdrop-filter: blur(15px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            .status-card.success {
                background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
                border-left: 4px solid #10b981;
            }
            .status-card.error {
                background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                border-left: 4px solid #ef4444;
            }
            .status-card.warning {
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                border-left: 4px solid #fbbf24;
            }
            .status-card .content {
                display: flex;
                align-items: center;
                gap: 10px;
                color: white;
                font-size: 14px;
                font-weight: 500;
            }
            header, footer { display: none !important; }
            .main {
                background: linear-gradient(135deg, #0d1b2a 0%, #000000 100%);
                color: #e0e1dd;
            }
            .main .block-container { padding: 2rem; }
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
                justify-content: center;
                align-items: center;
                transition: all 0.3s ease;
            }
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
                border-color: rgba(129, 153, 189, 0.4);
            }
            .feature-card .icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            .feature-card h3 {
                color: #ffffff;
                margin-bottom: 1rem;
                font-weight: 600;
            }
            .feature-card p {
                color: #a0aec0;
                line-height: 1.6;
            }
            .stats-container {
                background: rgba(27, 38, 59, 0.4);
                border-radius: 15px;
                padding: 2rem;
                margin: 2rem 0;
                border: 1px solid rgba(129, 153, 189, 0.2);
            }
            .storage-warning {
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                font-weight: 600;
            }
            .storage-warning.low {
                background: rgba(34, 197, 94, 0.2);
                border: 1px solid #22c55e;
                color: #22c55e;
            }
            .storage-warning.medium {
                background: rgba(251, 191, 36, 0.2);
                border: 1px solid #fbbf24;
                color: #fbbf24;
            }
            .storage-warning.high {
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid #ef4444;
                color: #ef4444;
            }
            .storage-progress {
                background: rgba(27, 38, 59, 0.4);
                border-radius: 10px;
                padding: 1.5rem;
                margin: 1rem 0;
            }
            .storage-progress h4 {
                color: #ffffff;
                margin-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

# --- 應用程式初始化 ---
def initialize_app():
    """初始化應用程式"""
    if 'page_selection' not in st.session_state:
        st.session_state.page_selection = "🏠 系統首頁"

def navigate_to(page_name):
    """導航到指定頁面"""
    st.session_state.page_selection = page_name
    st.rerun()

def show_home_page():
    st.markdown('<div class="title-container"><h1>北大文件比對與範本管理系統</h1><p>一個專業、高效的文件自動化解決方案</p></div>', unsafe_allow_html=True)

    # 顯示整合的雲端連接狀態卡片
    show_turso_status_card()

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
        
        if storage_stats.get('is_cloud', False):
            # 雲端模式：顯示 Turso 資料庫容量
            st.markdown(f'<h4>☁️ 雲端資料庫使用量：{storage_stats["formatted_size"]} ({storage_stats["usage_percentage"]}%)</h4>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.9em; color: #888;">📊 總容量限制：{storage_stats["cloud_limit_gb"]} GB</p>', unsafe_allow_html=True)
        else:
            # 本地模式：顯示本地存儲容量
            st.markdown(f'<h4>💾 本地儲存空間使用量：{storage_stats["formatted_size"]} ({storage_stats["usage_percentage"]}%)</h4>', unsafe_allow_html=True)
        
        st.progress(storage_stats['usage_percentage'] / 100)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 範本容量統計
        if storage_stats.get('is_cloud', False):
            # 雲端模式：顯示雲端範本統計
            st.markdown("---")
            st.subheader("📊 雲端範本容量統計")
            
            template_usage = storage_stats['template_usage']
            col1, col2 = st.columns(2)
            
            with col1:
                generation_stats = template_usage.get("智能生成範本", {})
                st.metric(
                    "🚀 智能生成範本", 
                    f"{generation_stats.get('size_mb', 0)} MB", 
                    f"{generation_stats.get('file_count', 0)} 個檔案"
                )
            
            with col2:
                comparison_stats = template_usage.get("比對範本", {})
                st.metric(
                    "🔍 比對範本", 
                    f"{comparison_stats.get('size_mb', 0)} MB", 
                    f"{comparison_stats.get('file_count', 0)} 個檔案"
                )
            
            st.info("💡 **提示**：所有範本已統一保存到雲端，定期備份即可")
        else:
            # 本地模式：顯示本地範本統計
            st.markdown("---")
            st.subheader("📊 本地範本容量統計")
            
            template_usage = storage_stats.get('template_usage', {})
            col1, col2 = st.columns(2)
            
            with col1:
                generation_stats = template_usage.get("智能生成範本", {})
                st.metric(
                    "🚀 智能生成範本", 
                    f"{generation_stats.get('size_mb', 0)} MB", 
                    f"{generation_stats.get('file_count', 0)} 個檔案"
                )
            
            with col2:
                comparison_stats = template_usage.get("比對範本", {})
                st.metric(
                    "🔍 比對範本", 
                    f"{comparison_stats.get('size_mb', 0)} MB", 
                    f"{comparison_stats.get('file_count', 0)} 個檔案"
                )
            
            st.warning("⚠️ 本地模式：建議配置雲端資料庫以獲得更好的容量管理")
                    
    except Exception as e:
        st.warning(f"容量監控載入失敗：{str(e)}")

def show_comparison_page():
    from views.document_comparison import show_document_comparison_main
    show_document_comparison_main()

# --- 主程式 (邏輯已更新) ---
def main():
    apply_global_styles()
    initialize_app()
    
    # 檢查 Turso 狀態（靜默模式，不顯示訊息）
    try:
        from core.turso_database import TursoDatabase
        turso_db = TursoDatabase()
        # 靜默檢查，不顯示狀態訊息
        turso_db.is_cloud_mode()  # 只檢查狀態，不顯示訊息
    except Exception as e:
        # 只在出現錯誤時顯示警告
        st.warning(f"資料庫狀態檢查失敗：{str(e)}")
    
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
