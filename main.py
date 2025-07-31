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
# 為了讓主程式能獨立顯示，我們將導入放在 try-except 中
try:
    from core.template_manager import TemplateManager
    from config.template_config import TemplateConfig, TemplateVariableParser
    # 檢查並導入 PDF 相關模組
    from pages.pdf_annotation_interface import pdf_annotation_interface
    # 導入響應式UI組件
    from utils.ui_components import apply_custom_css
except ImportError:
    # 在這個主檔案中，我們可以允許導入失敗，以便單獨檢視主頁面佈局
    # 具體的功能頁面會在被選中時才嘗試載入
    def apply_custom_css():
        """響應式CSS樣式備用版本"""
        st.markdown("""
        <style>
        @media (max-width: 768px) {
            .main .block-container { padding: 0.5rem; }
            .stButton > button { width: 100% !important; }
            h1 { font-size: 1.8rem !important; }
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)


def setup_page_config():
    """設定響應式頁面配置"""
    st.set_page_config(
        page_title="📄 PDF文件比對與範本管理系統",
        page_icon="📄",
        layout="wide",  # 恢復原本的wide布局
        initial_sidebar_state="expanded",  # 電腦版預設展開側邊欄
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "📄 PDF文件比對與範本管理系統 v3.0 - 響應式優化版"
        }
    )
    
    hide_streamlit_style = """
    <style>
    /* 隱藏自動生成的導覽連結 */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* 隱藏不需要的元素 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    
    /* 美化按鈕 */
    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #45a049) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
    }
    
    /* 功能卡片樣式 */
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
    
    /* 範本卡片樣式 */
    .template-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
        index=st.session_state.get('page_selection_index', 0) # 預設顯示首頁
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
                del st.session_state['page_selection']  # 清除狀態
        except:
            pass
    
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

def home_page_tab():
    """系統首頁功能"""
    try:
        from pages.home_page import show_home_page
        show_home_page()
    except ImportError:
        st.error("❌ 無法載入首頁模組。請確認 `pages/home_page.py` 檔案存在。")
    except Exception as e:
        st.error(f"執行首頁功能時發生錯誤：{e}")

def file_input_generation_tab():
    """檔案輸入與生成功能"""
    try:
        from pages.file_input_generator import file_input_generation_page
        file_input_generation_page()
    except ImportError:
        st.error("❌ 無法載入檔案輸入與生成模組。請確認 `pages/file_input_generator.py` 檔案存在。")
    except Exception as e:
        st.error(f"執行檔案輸入與生成功能時發生錯誤：{e}")

def template_settings_tab():
    """範本管理設定功能"""
    try:
        from pages.template_settings import template_settings_page
        template_settings_page()
    except ImportError:
        st.error("❌ 無法載入範本設定模組。請確認 `pages/template_settings.py` 檔案存在。")
    except Exception as e:
        st.error(f"執行範本設定功能時發生錯誤：{e}")

def pdf_annotation_tab():
    """PDF 變數標記功能"""
    try:
        from pages.pdf_annotation_interface import pdf_annotation_interface
        pdf_annotation_interface()
    except ImportError:
        st.error("❌ 無法載入 PDF 變數標記模組。請確認 `pages/pdf_annotation_interface.py` 檔案存在。")
    except Exception as e:
        st.error(f"執行 PDF 變數標記功能時發生錯誤：{e}")


def document_comparison_tab():
    """文件比對檢查功能"""
    try:
        from pages.document_comparison import document_comparison_page
        document_comparison_page()
    except ImportError:
        st.error("❌ 無法載入文件比對模組。請確認 `pages/document_comparison.py` 檔案存在。")
    except Exception as e:
        st.error(f"執行文件比對功能時發生錯誤：{e}")


def document_generator_tab():
    """智能文件生成功能"""
    try:
        from pages.document_generator import document_generator_tab
        document_generator_tab()
    except ImportError:
        st.error("❌ 無法載入智能文件生成模組。請確認 `pages/document_generator.py` 檔案存在。")
    except Exception as e:
        st.error(f"執行智能文件生成功能時發生錯誤：{e}")


def main():
    """主應用程式進入點"""
    setup_page_config()
    
    # 啟用響應式設計（包含手機版優化）
    apply_custom_css()
    
    function_choice, _, _, _, _ = sidebar_content()
    
    # 根據選擇顯示對應功能
    if function_choice == "🏠 系統首頁":
        home_page_tab()
    elif function_choice == "🎨 PDF 變數標記":
        pdf_annotation_tab()
    elif function_choice == "📝 檔案輸入與生成":
        file_input_generation_tab()
    elif function_choice == "🔍 文件比對檢查":
        document_comparison_tab()
    elif function_choice == "⚙️ 範本管理設定":
        template_settings_tab()
    elif function_choice == "📄 智能文件生成":
        document_generator_tab()
    
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            📄 北大PDF文件比對與範本管理系統 v3.0 (手機優化版) | 
            🕒 最後更新：{datetime.now().strftime("%Y-%m-%d %H:%M")}
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()