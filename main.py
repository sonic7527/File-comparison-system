# 檔名: main.py
# (這是完整的、已加入安全隱藏規則的最終版本)

"""
智慧文件處理與範本管理系統 - Streamlit 版本
整合文件比較、範本管理、資料分析等功能
"""
import streamlit as st
import pandas as pd
import io
import base64
from datetime import datetime
import json
import sys
import os

# 添加專案路徑到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入自定義模組
from utils.ui_components import apply_custom_css, mobile_navigation_bar, mobile_page_switch
from pages.home_page import show_home_page
from pages.pdf_annotation_interface import pdf_annotation_interface
from pages.file_input_generator import file_input_generation_page
from pages.document_comparison import document_comparison_page
from pages.template_settings import template_settings_page
from pages.document_generator import document_generator_tab

def setup_page_config():
    """設定響應式頁面配置"""
    st.set_page_config(
        page_title="📄 PDF文件比對與範本管理系統",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="auto", # 電腦版展開，手機版自動隱藏
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "📄 PDF文件比對與範本管理系統 v3.1 - 手機優化版"
        }
    )

def device_detector_js():
    """返回一個JavaScript片段，用於檢測設備類型並將其存儲在sessionStorage中。"""
    return """
    <script>
    (function() {
        if (!sessionStorage.getItem('device_type')) {
            const userAgent = navigator.userAgent;
            const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
            const device_type = isMobile ? 'mobile' : 'desktop';
            sessionStorage.setItem('device_type', device_type);
            
            // 僅在第一次檢測時重新整理頁面以觸發Python後端
            window.location.reload();
        }
    })();
    </script>
    """

def get_device_type():
    """從 session_state 獲取設備類型 """
    # 使用 st.experimental_get_query_params() 是一種間接方式
    # 更可靠的方式是讓 JS 設置一個標記然後重新整理
    # 在這裡，我們將依賴於JS腳本重載頁面後的一些狀態
    # 這是Streamlit的一個局限，但我們可以用下面的方式模擬
    js = device_detector_js()
    st.components.v1.html(js, height=0)

    # 這裡我們不能直接從JS讀取，所以我們將依賴客戶端重載
    # 實際設備類型的判斷，將基於是否顯示手機導航欄
    # 這裡我們先假設一個預設值，並讓前端CSS處理顯示/隱藏
    return "desktop" # 預設為桌面，讓CSS處理

def desktop_sidebar():
    """桌面版側邊欄"""
    st.sidebar.markdown("## 🛠️ 功能選單")
    
    PAGES = [
        "🏠 系統首頁",
        "🎨 PDF 變數標記",
        "📝 檔案輸入與生成", 
        "🔍 文件比對檢查", 
        "⚙️ 範本管理設定",
        "📄 智能文件生成"
    ]

    if 'page_selection' not in st.session_state:
        st.session_state['page_selection'] = PAGES[0]

    choice = st.sidebar.radio(
        "選擇功能",
        options=PAGES,
        key="desktop_nav"
    )
    st.session_state['page_selection'] = choice
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ 系統設定")
    st.sidebar.slider("最大檔案大小 (MB)", 1, 100, 10, key="file_size")
    st.sidebar.multiselect(
        "允許的檔案格式",
        ["PDF", "PNG", "JPG"],
        default=["PDF", "PNG"],
        key="file_formats"
    )

def main():
    """主應用程式進入點"""
    setup_page_config()
    apply_custom_css()
    
    # --- 設備檢測與導航 ---
    # 默認在所有設備上顯示側邊欄，讓CSS控制其可見性
    desktop_sidebar()

    # 僅在手機上顯示底部導航
    st.markdown('<div class="mobile-only">', unsafe_allow_html=True)
    mobile_navigation_bar()
    mobile_page_switch()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- 頁面渲染 ---
    current_page = st.session_state.get('page_selection', "🏠 系統首頁")

    if current_page == "🏠 系統首頁":
        show_home_page()
    elif current_page == "🎨 PDF 變數標記":
        pdf_annotation_interface()
    elif current_page == "📝 檔案輸入與生成":
        file_input_generation_page()
    elif current_page == "🔍 文件比對檢查":
        document_comparison_page()
    elif current_page == "⚙️ 範本管理設定":
        template_settings_page()
    elif current_page == "📄 智能文件生成":
        document_generator_tab()

    # --- 頁腳 ---
    st.markdown(
        f"""
        <div style='text-align: center; color: #888; padding: 2rem 0; font-size: 0.9rem;'>
            <p>北大文件比對與範本管理系統 v3.1 | 最後更新：{datetime.now().strftime("%Y-%m-%d")}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    # 使用JS注入來檢測設備類型
    # 這是一個啟動技巧：首次加載時注入JS，JS會存儲設備類型並重新加載。
    # 之後的加載將會有設備類型的信息。
    st.components.v1.html(device_detector_js(), height=0)
    main()
