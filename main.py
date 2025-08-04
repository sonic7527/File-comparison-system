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
        st.markdown(f'<h4>💾 儲存空間使用量：{storage_stats["formatted_size"]} ({storage_stats["usage_percentage"]}%)</h4>', unsafe_allow_html=True)
        st.progress(storage_stats['usage_percentage'] / 100)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 雲端容量統計
        try:
            from core.turso_database import TursoDatabase
            turso_db = TursoDatabase()
            
            if turso_db.is_cloud_mode():
                turso_db.create_tables()
                
                # 獲取比對範本統計
                comparison_templates = turso_db.get_comparison_templates()
                comparison_size = sum(template.get('file_size', 0) for template in comparison_templates)
                comparison_size_mb = round(comparison_size / (1024 * 1024), 2)
                
                # 獲取智能生成範本統計
                template_groups = turso_db.get_all_template_groups_cloud()
                template_files = []
                for group in template_groups:
                    files = turso_db.get_template_files_cloud(group['id'])
                    template_files.extend(files)
                
                generation_size = sum(file.get('file_size', 0) for file in template_files)
                generation_size_mb = round(generation_size / (1024 * 1024), 2)
                
                st.markdown("---")
                st.subheader("📊 雲端範本容量統計")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "🚀 智能生成範本", 
                        f"{generation_size_mb} MB", 
                        f"{len(template_files)} 個檔案"
                    )
                
                with col2:
                    st.metric(
                        "🔍 比對範本", 
                        f"{comparison_size_mb} MB", 
                        f"{len(comparison_templates)} 個檔案"
                    )
                
                st.info("💡 **提示**：所有範本已統一保存到雲端，定期備份即可")
            else:
                st.warning("⚠️ 雲端未連接，無法顯示容量統計")
        except Exception as e:
            st.warning(f"容量統計載入失敗：{str(e)}")
                    
    except Exception as e:
        st.warning("容量監控暫時無法載入，請稍後再試")

def show_comparison_page():
    from views.document_comparison import show_document_comparison_main
    show_document_comparison_main()

# --- 主程式 (邏輯已更新) ---
def main():
    apply_global_styles()
    initialize_app()
    
    # 檢查並顯示 Turso 狀態
    try:
        from core.turso_database import TursoDatabase
        turso_db = TursoDatabase()
        # 安全檢查方法是否存在
        if hasattr(turso_db, 'check_and_display_status'):
            turso_db.check_and_display_status()
        else:
            # 如果方法不存在，顯示基本狀態
            if turso_db.is_cloud_mode():
                st.success("✅ Turso 雲端資料庫已配置")
            else:
                st.warning("⚠️ 未配置 Turso，將使用本地 SQLite")
    except Exception as e:
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
