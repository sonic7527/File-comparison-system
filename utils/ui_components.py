import streamlit as st

def apply_custom_css():
    """套用自定義CSS樣式"""
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton > button {
            border-radius: 10px;
            padding: 0.5rem 1rem;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab-list"] button {
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background: #4CAF50;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

def show_status_card(status_type: str, message: str):
    """
    顯示單一狀態卡片
    status_type: 'success', 'error', 'warning'
    message: 顯示訊息
    """
    status_icons = {
        'success': '✅',
        'error': '❌', 
        'warning': '⚠️'
    }
    
    icon = status_icons.get(status_type, 'ℹ️')
    
    st.markdown(f"""
    <div class="status-card {status_type}">
        <div class="content">
            <span>{icon}</span>
            <span>{message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_turso_status_card():
    """
    顯示整合的 Turso 狀態卡片，包含所有相關狀態
    """
    from core.turso_database import TursoDatabase
    
    try:
        turso_db = TursoDatabase()
        # 靜默檢查狀態，不觸發任何訊息顯示
        if turso_db.is_configured():
            # 整合所有成功狀態
            status_messages = [
                "✅ Turso 配置正確，已準備連接雲端資料庫",
                "🌐 雲端模式：範本將同步到雲端資料庫", 
                "✅ Turso 表格創建成功"
            ]
            
            st.markdown(f"""
            <div class="status-card success-dark">
                <div class="content">
                    <span>☁️</span>
                    <span>雲端連接正常 | 純雲端模式</span>
                </div>
                <div style="margin-top: 8px; font-size: 10px; opacity: 0.8;">
                    {status_messages[0]}<br>
                    {status_messages[1]}<br>
                    {status_messages[2]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-card error-dark">
                <div class="content">
                    <span>❌</span>
                    <span>雲端未連接，請檢查配置</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception:
        st.markdown(f"""
        <div class="status-card warning-dark">
            <div class="content">
                <span>⚠️</span>
                <span>雲端連接狀態未知</span>
            </div>
        </div>
        """, unsafe_allow_html=True)