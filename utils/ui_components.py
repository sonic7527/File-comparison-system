# 檔名: utils/ui_components.py
# 用於存放可重用的UI組件和樣式

import streamlit as st
import os

def apply_custom_css():
    """載入並應用所有自定義CSS文件"""
    
    # --- 核心CSS ---
    core_css = """
    <style>
    /* 隱藏 Streamlit 的預設選單和頁腳 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}

    /* 隱藏 Streamlit 自動生成的側邊欄導航 */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* 統一卡片樣式 */
    .feature-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .feature-card h3 {
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    .feature-card ul {
        list-style: none;
        padding-left: 0;
    }
    
    .feature-card li {
        padding: 0.3rem 0;
        color: #34495e;
        font-weight: 500;
    }
    </style>
    """
    st.markdown(core_css, unsafe_allow_html=True)

def mobile_navigation_bar():
    """手機版底部導航列 - 暫時停用"""
    pass

def mobile_page_switch():
    """手機版頁面切換 - 暫時停用"""
    pass
