# 檔名: pages/mobile_home.py
# 手機版專用首頁 - iOS風格設計

import streamlit as st

def show_mobile_home():
    """顯示手機版首頁 - iOS風格"""
    
    # iOS風格CSS
    st.markdown("""
    <style>
    /* iOS風格樣式 */
    .main .block-container {
        padding: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* iOS風格卡片 */
    .ios-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .ios-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* iOS風格按鈕 */
    .ios-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        border: none;
        font-weight: 600;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        width: 100%;
        text-align: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .ios-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* iOS風格標題 */
    .ios-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* iOS風格圖標 */
    .ios-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: block;
        text-align: center;
    }
    
    /* iOS風格狀態欄 */
    .ios-status-bar {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 0.5rem 1rem;
        border-radius: 0 0 15px 15px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
        color: #333;
    }
    
    /* iOS風格導航 */
    .ios-nav {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* iOS風格功能卡片 */
    .ios-feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .ios-feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
    }
    
    /* 隱藏Streamlit預設元素 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    </style>
    """, unsafe_allow_html=True)
    
    # iOS風格狀態欄
    st.markdown("""
    <div class="ios-status-bar">
        📱 北大文件比對系統
    </div>
    """, unsafe_allow_html=True)
    
    # iOS風格標題卡片
    st.markdown("""
    <div class="ios-card">
        <div class="ios-title" style="font-size: 2rem;">
            📄 文件比對系統
        </div>
        <p style="text-align: center; color: #666; font-size: 1rem; margin: 0;">
            智慧化的文件處理解決方案
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # iOS風格功能導航
    st.markdown("## 🚀 功能選單")
    
    # 功能卡片網格
    col1, col2 = st.columns(2)
    
    with col1:
        # PDF標記卡片
        st.markdown("""
        <div class="ios-feature-card">
            <div class="ios-icon">🎨</div>
            <h3 style="text-align: center; margin: 0.5rem 0;">PDF標記</h3>
            <p style="text-align: center; margin: 0; font-size: 0.9rem; opacity: 0.9;">
                標記PDF變數
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎨 PDF標記", key="mobile_pdf", use_container_width=True):
            st.session_state['mobile_page'] = "pdf_annotation"
            st.experimental_rerun()
        
        # 檔案生成卡片
        st.markdown("""
        <div class="ios-feature-card">
            <div class="ios-icon">📝</div>
            <h3 style="text-align: center; margin: 0.5rem 0;">檔案生成</h3>
            <p style="text-align: center; margin: 0; font-size: 0.9rem; opacity: 0.9;">
                生成標準文件
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 檔案生成", key="mobile_generate", use_container_width=True):
            st.session_state['mobile_page'] = "file_generate"
            st.experimental_rerun()
    
    with col2:
        # 比對檢查卡片
        st.markdown("""
        <div class="ios-feature-card">
            <div class="ios-icon">🔍</div>
            <h3 style="text-align: center; margin: 0.5rem 0;">比對檢查</h3>
            <p style="text-align: center; margin: 0; font-size: 0.9rem; opacity: 0.9;">
                文件比對分析
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 比對檢查", key="mobile_compare", use_container_width=True):
            st.session_state['mobile_page'] = "document_compare"
            st.experimental_rerun()
        
        # 系統設定卡片
        st.markdown("""
        <div class="ios-feature-card">
            <div class="ios-icon">⚙️</div>
            <h3 style="text-align: center; margin: 0.5rem 0;">系統設定</h3>
            <p style="text-align: center; margin: 0; font-size: 0.9rem; opacity: 0.9;">
                管理系統設定
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚙️ 系統設定", key="mobile_settings", use_container_width=True):
            st.session_state['mobile_page'] = "settings"
            st.experimental_rerun()
    
    # iOS風格切換按鈕
    st.markdown("---")
    st.markdown("""
    <div class="ios-card">
        <p style="text-align: center; color: #666; margin-bottom: 1rem;">
            需要更多功能？切換到電腦版
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🖥️ 切換到電腦版", key="switch_to_desktop", use_container_width=True):
        st.session_state['mobile_mode'] = False
        st.experimental_rerun()
    
    # iOS風格頁腳
    st.markdown("""
    <div class="ios-card" style="text-align: center; padding: 1rem;">
        <p style="color: #888; font-size: 0.9rem; margin: 0;">
            📱 iOS風格手機版 v3.0
        </p>
    </div>
    """, unsafe_allow_html=True)

def mobile_pdf_annotation():
    """手機版PDF標記頁面 - iOS風格"""
    st.markdown("""
    <style>
    .ios-back-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        border: none;
        font-weight: 600;
        padding: 0.8rem 1.5rem;
        margin: 1rem 0;
        width: 100%;
        text-align: center;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 🎨 PDF 變數標記")
    st.markdown("""
    <div class="ios-card">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎨</div>
            <h3>PDF 變數標記</h3>
            <p style="color: #666;">在PDF文件上標記變數位置</p>
        </div>
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            <p style="margin: 0; color: #666;">📱 手機版PDF標記功能正在開發中...</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔙 返回首頁", key="mobile_pdf_back", use_container_width=True):
        st.session_state['mobile_page'] = "home"
        st.experimental_rerun()

def mobile_file_generate():
    """手機版檔案生成頁面 - iOS風格"""
    st.markdown("## 📝 檔案輸入與生成")
    st.markdown("""
    <div class="ios-card">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📝</div>
            <h3>檔案輸入與生成</h3>
            <p style="color: #666;">根據範本生成標準化文件</p>
        </div>
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            <p style="margin: 0; color: #666;">📱 手機版檔案生成功能正在開發中...</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔙 返回首頁", key="mobile_generate_back", use_container_width=True):
        st.session_state['mobile_page'] = "home"
        st.experimental_rerun()

def mobile_document_compare():
    """手機版文件比對頁面 - iOS風格"""
    st.markdown("## 🔍 文件比對檢查")
    st.markdown("""
    <div class="ios-card">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
            <h3>文件比對檢查</h3>
            <p style="color: #666;">比對文件差異與完整性</p>
        </div>
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            <p style="margin: 0; color: #666;">📱 手機版文件比對功能正在開發中...</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔙 返回首頁", key="mobile_compare_back", use_container_width=True):
        st.session_state['mobile_page'] = "home"
        st.experimental_rerun()

def mobile_settings():
    """手機版設定頁面 - iOS風格"""
    st.markdown("## ⚙️ 系統設定")
    st.markdown("""
    <div class="ios-card">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚙️</div>
            <h3>系統設定</h3>
            <p style="color: #666;">管理系統參數與偏好設定</p>
        </div>
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            <p style="margin: 0; color: #666;">📱 手機版設定功能正在開發中...</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔙 返回首頁", key="mobile_settings_back", use_container_width=True):
        st.session_state['mobile_page'] = "home"
        st.experimental_rerun()

def mobile_main():
    """手機版主程式"""
    # 初始化手機版狀態
    if 'mobile_page' not in st.session_state:
        st.session_state['mobile_page'] = "home"
    
    # 根據選擇顯示對應頁面
    if st.session_state['mobile_page'] == "home":
        show_mobile_home()
    elif st.session_state['mobile_page'] == "pdf_annotation":
        mobile_pdf_annotation()
    elif st.session_state['mobile_page'] == "file_generate":
        mobile_file_generate()
    elif st.session_state['mobile_page'] == "document_compare":
        mobile_document_compare()
    elif st.session_state['mobile_page'] == "settings":
        mobile_settings()

if __name__ == "__main__":
    st.set_page_config(
        page_title="📱 北大文件比對系統 - 手機版",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    mobile_main() 