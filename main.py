# 檔名: main.py
# (這是恢復到原本樣式的版本)

import streamlit as st
from datetime import datetime
import sys
import os

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入自定義模組
from utils.ui_components import apply_custom_css
from pages.home_page import show_home_page
from pages.pdf_annotation_interface import pdf_annotation_interface
from pages.file_input_generator import file_input_generation_page
from pages.document_comparison import document_comparison_page
from pages.template_settings import template_settings_page
from pages.document_generator import document_generator_tab

def setup_page_config():
    """設定頁面配置 (必須是第一個執行的 Streamlit 命令)"""
    st.set_page_config(
        page_title="📄 PDF文件比對與範本管理系統",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "📄 PDF文件比對與範本管理系統 v3.0"
        }
    )

def sidebar_content():
    """側邊欄內容"""
    st.sidebar.markdown("## 🛠️ 功能選單")
    
    # 功能選擇
    function_choice = st.sidebar.selectbox(
        "選擇功能",
        [
            "🏠 系統首頁",
            "🎨 PDF 變數標記",
            "📝 檔案輸入與生成", 
            "🔍 文件比對檢查", 
            "⚙️ 範本管理設定",
            "📄 智能文件生成"
        ],
        index=st.session_state.get('page_selection_index', 0)
    )
    
    # 如果有頁面選擇狀態，更新選擇
    if 'page_selection' in st.session_state:
        try:
            options = [
                "🏠 系統首頁",
                "🎨 PDF 變數標記",
                "📝 檔案輸入與生成", 
                "🔍 文件比對檢查", 
                "⚙️ 範本管理設定",
                "📄 智能文件生成"
            ]
            if st.session_state['page_selection'] in options:
                function_choice = st.session_state['page_selection']
                st.session_state['page_selection_index'] = options.index(function_choice)
                del st.session_state['page_selection']
        except:
            pass
    
    st.sidebar.markdown("---")
    
    # 手機版切換按鈕
    st.sidebar.markdown("### 📱 手機版")
    if st.sidebar.button("📱 切換到手機版", use_container_width=True):
        st.session_state['mobile_mode'] = True
        st.experimental_rerun()
    
    st.sidebar.markdown("---")
    
    # 檔案上傳設定
    st.sidebar.markdown("### 📁 檔案設定")
    max_file_size = st.sidebar.slider("最大檔案大小 (MB)", 1, 100, 10)
    allowed_formats = st.sidebar.multiselect(
        "允許的檔案格式",
        ["CSV", "Excel", "TXT", "JSON", "PDF"],
        default=["CSV", "Excel", "TXT", "PDF"]
    )
    
    st.sidebar.markdown("---")
    
    # 處理選項
    st.sidebar.markdown("### ⚙️ 處理選項")
    auto_process = st.sidebar.checkbox("自動處理", value=True)
    show_preview = st.sidebar.checkbox("顯示預覽", value=True)
    
    return function_choice, max_file_size, allowed_formats, auto_process, show_preview

def main():
    """主應用程式進入點"""
    setup_page_config()
    
    # 檢查是否要切換到手機版
    if st.session_state.get('mobile_mode', False):
        from pages.mobile_home import mobile_main
        mobile_main()
    else:
        # 電腦版邏輯
        desktop_main()

def desktop_main():
    """電腦版主應用程式"""
    # 應用自定義CSS
    apply_custom_css()
    
    function_choice, _, _, _, _ = sidebar_content()
    
    # 根據選擇顯示對應功能
    if function_choice == "🏠 系統首頁":
        show_home_page()
    elif function_choice == "🎨 PDF 變數標記":
        pdf_annotation_interface()
    elif function_choice == "📝 檔案輸入與生成":
        file_input_generation_page()
    elif function_choice == "🔍 文件比對檢查":
        document_comparison_page()
    elif function_choice == "⚙️ 範本管理設定":
        template_settings_page()
    elif function_choice == "📄 智能文件生成":
        document_generator_tab()
    
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            📄 北大PDF文件比對與範本管理系統 v3.0 | 
            🕒 最後更新：{datetime.now().strftime("%Y-%m-%d %H:%M")}
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
