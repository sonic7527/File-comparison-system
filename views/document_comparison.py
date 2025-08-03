import streamlit as st
import os
import pandas as pd
import sqlite3
import json
import shutil
import tempfile
from datetime import datetime
from PIL import Image
import io
from core.database import get_db_connection, init_database # 引入 init_database
from pathlib import Path # 引入 pathlib

# --- 核心修改區域 START ---
# 建立一個指向專案根目錄的絕對路徑
ROOT_DIR = Path(__file__).parent.parent 

def setup_comparison_database():
    """
    設置比對範本資料庫 - 使用統一的資料庫和穩定的相對路徑
    """
    # 確保資料庫和表格已創建
    init_database()  
    
    # 無論在哪個系統，都使用專案內部的 data/comparison_templates 資料夾
    templates_dir = ROOT_DIR / "data" / "comparison_templates"
    
    os.makedirs(templates_dir, exist_ok=True)
    
    return templates_dir
# --- 核心修改區域 END ---

def save_comparison_template(name: str, description: str, uploaded_file, file_type: str) -> int:
    """
    儲存比對範本 (支援本地和雲端同步)
    """
    try:
        templates_dir = setup_comparison_database()
        
        # 獲取文件大小
        uploaded_file.seek(0, 2)
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)
        
        # 本地保存
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 先插入紀錄，取得 ID
            cursor.execute(
                "INSERT INTO comparison_templates (name, filename, filepath, file_type, file_size) VALUES (?, ?, ?, ?, ?)",
                (name, uploaded_file.name, "", file_type, file_size)
            )
            template_id = cursor.lastrowid
            
            # 使用 pathlib 組合路徑
            file_extension = Path(uploaded_file.name).suffix
            template_filename = f"{template_id}_{name}{file_extension}"
            template_path = templates_dir / template_filename
            
            # 儲存實體檔案
            with open(template_path, 'wb') as f:
                f.write(uploaded_file.read())
            
            # 將穩定的相對路徑存回資料庫
            relative_path = str(template_path.relative_to(ROOT_DIR))
            
            cursor.execute(
                "UPDATE comparison_templates SET filepath = ? WHERE id = ?",
                (relative_path, template_id)
            )
            conn.commit()
        
        # 嘗試同步到雲端
        try:
            from core.turso_database import turso_db
            from core.github_storage import github_storage
            
            if turso_db.is_cloud_mode():
                # 上傳檔案到 GitHub
                if github_storage.is_cloud_mode():
                    github_url = github_storage.upload_file(str(template_path), template_filename)
                    if github_url:
                        # 保存到 Turso
                        turso_db.save_comparison_template(
                            name=name,
                            filename=uploaded_file.name,
                            filepath=github_url,  # 使用 GitHub URL
                            file_type=file_type,
                            file_size=file_size
                        )
                        st.success("✅ 範本已同步到雲端")
                    else:
                        st.warning("⚠️ 檔案上傳到 GitHub 失敗，但本地保存成功")
                else:
                    st.warning("⚠️ GitHub 存儲未配置，僅保存到本地")
        except Exception as e:
            st.warning(f"⚠️ 雲端同步失敗，但本地保存成功: {str(e)}")
        
        return template_id
    except sqlite3.IntegrityError:
        st.error(f"範本儲存錯誤：範本名稱 '{name}' 已存在。")
        return -1
    except Exception as e:
        st.error(f"範本儲存錯誤：{str(e)}")
        return -1

def get_comparison_templates() -> list:
    """
    獲取所有比對範本 (支援 Turso 和本地 SQLite)
    """
    try:
        # 嘗試使用 Turso 雲端資料庫
        from core.turso_database import turso_db
        
        if turso_db.is_cloud_mode():
            # 雲端模式：使用 Turso
            turso_db.create_tables()
            templates = turso_db.get_comparison_templates()
            
            # 顯示雲端統計
            st.info(f"🌐 雲端範本數量: {len(templates)}")
            return templates
        else:
            # 本地模式：使用 SQLite
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM comparison_templates ORDER BY created_at DESC")
                templates = [dict(row) for row in cursor.fetchall()]
                
                # 顯示本地統計
                st.info(f"💻 本地範本數量: {len(templates)}")
                return templates
    except Exception as e:
        st.error(f"取得範本列表錯誤：{str(e)}")
        return []

def delete_comparison_template(template_id: int) -> bool:
    """
    刪除比對範本 (已修正路徑處理)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM comparison_templates WHERE id = ?", (template_id,))
            result = cursor.fetchone()
            
            if result:
                # 組合出絕對路徑來刪除檔案
                relative_path = result[0]
                absolute_path = ROOT_DIR / relative_path
                
                if absolute_path.exists():
                    os.remove(absolute_path)
                
                cursor.execute("DELETE FROM comparison_templates WHERE id = ?", (template_id,))
                conn.commit()
                return True
        return False
    except Exception as e:
        st.error(f"刪除範本錯誤：{str(e)}")
        return False

# ... 以下是您的 UI 顯示函數，保持不變 ...
# (為了簡潔，此處省略，請您保留您檔案中原有的 UI 函數)
def show_document_comparison():
    st.title("🔍 文件比對檢查系統")
    st.markdown("---")
    try:
        from utils.storage_monitor import get_template_storage_usage
        template_usage = get_template_storage_usage()
        if "比對範本" in template_usage:
            comp_usage = template_usage["比對範本"]
            st.info(f"📊 **比對範本容量**：{comp_usage['size_mb']} MB ({comp_usage['file_count']} 個檔案)")
    except Exception as e:
        st.warning("容量統計載入失敗，請稍後再試")
    st.markdown("---")
    st.subheader("📋 選擇操作模式")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📤 上傳範本\n**功能**：上傳並保存比對用的參考範本\n\n**流程**：\n- 上傳參考範本文件\n- 為範本命名\n- 保存到範本庫\n- 可重複使用")
        if st.button("📤 上傳範本", use_container_width=True, type="primary"):
            st.session_state.comparison_mode = "upload_template"
            st.session_state.comparison_step = "upload_reference"
            st.rerun()
    with col2:
        st.markdown("### 📁 管理範本\n**功能**：管理已上傳的比對範本\n\n**功能**：\n- 查看已上傳的範本\n- 刪除不需要的範本\n- 範本容量統計\n- 範本分類管理")
        if st.button("📁 管理範本", use_container_width=True, type="primary"):
            st.session_state.comparison_mode = "manage_templates"
            st.session_state.comparison_step = "template_list"
            st.rerun()
    with col3:
        st.markdown("### 🔍 比對範本\n**功能**：使用已保存的範本進行文件比對\n\n**流程**：\n- 選擇比對模式\n- 選擇已保存的範本\n- 上傳需要比對的文件\n- 查看比對結果")
        if st.button("🔍 比對範本", use_container_width=True, type="primary"):
            st.session_state.comparison_mode = "compare_templates"
            st.session_state.comparison_step = "select_mode"
            st.session_state.comparison_type = None
            st.session_state.selected_template = None
            st.session_state.target_file = None
            st.rerun()
    st.markdown("---")
    st.subheader("📖 使用說明")
    with st.expander("💡 支援的文件格式"):
        st.markdown("...") # 省略
    with st.expander("⚙️ 技術說明"):
        st.markdown("...") # 省略

def show_template_upload():
    st.title("📤 上傳比對範本")
    st.markdown("---")
    if st.session_state.comparison_step == "upload_reference":
        st.subheader("📤 步驟 1：上傳參考範本")
        st.info("請上傳一個標準的參考範本，系統將保存此範本供日後比對使用。")
        template_name = st.text_input("範本名稱", help="為這個比對範本命名，例如「標準合約範本」")
        uploaded_reference = st.file_uploader("選擇參考範本文件", type=['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'xls'], help="支援PDF、圖片、Word、Excel格式")
        if uploaded_reference and template_name:
            with st.spinner("正在處理上傳的範本..."):
                try:
                    file_extension = os.path.splitext(uploaded_reference.name)[1].lower()
                    file_type_map = {'.pdf':'PDF', '.png':'PNG', '.jpg':'JPG', '.jpeg':'JPEG', '.docx':'DOCX', '.xlsx':'XLSX', '.xls':'XLS'}
                    file_type = file_type_map.get(file_extension, 'UNKNOWN')
                    progress_bar = st.progress(0)
                    progress_bar.progress(25)
                    template_id = save_comparison_template(name=template_name, description=f"比對範本：{uploaded_reference.name}", uploaded_file=uploaded_reference, file_type=file_type)
                    progress_bar.progress(100)
                    if template_id > 0:
                        st.success(f"✅ 範本已成功儲存：{template_name}")
                        st.session_state.saved_template_id = template_id
                        st.session_state.template_name = template_name
                        st.session_state.comparison_step = "save_template"
                        st.rerun()
                    else:
                        st.error("範本儲存失敗，請重試")
                except Exception as e:
                    st.error(f"上傳失敗：{str(e)}")
        elif uploaded_reference and not template_name:
            st.warning("請輸入範本名稱")
        elif template_name and not uploaded_reference:
            st.warning("請上傳範本文件")
    elif st.session_state.comparison_step == "save_template":
        st.subheader("📤 步驟 2：保存範本")
        if hasattr(st.session_state, 'saved_template_id') and st.session_state.saved_template_id > 0:
            template_name = st.session_state.get('template_name', '未知範本')
            st.success(f"✅ 範本已成功保存：{template_name}")
            st.info(f"📝 範本ID：{st.session_state.saved_template_id}")
            st.info("此範本已保存到範本庫，您可以在「比對範本」時選擇使用。")
        else:
            st.error("範本保存失敗，請重試")
        st.markdown("---")
        st.subheader("🔍 下一步操作")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📤 繼續上傳範本", use_container_width=True, type="primary"):
                st.session_state.comparison_step = "upload_reference"
                st.session_state.saved_template_id = None
                st.session_state.template_name = None
                st.rerun()
        with col2:
            if st.button("🔍 立即開始比對", use_container_width=True, type="primary"):
                st.session_state.comparison_mode = "compare_templates"
                st.session_state.comparison_step = "select_mode"
                st.rerun()
        with col3:
            if st.button("⬅️ 返回主選單", use_container_width=True):
                st.session_state.comparison_mode = None
                st.session_state.comparison_step = None
                st.session_state.saved_template_id = None
                st.session_state.template_name = None
                st.rerun()

def show_template_management():
    st.title("📁 管理比對範本")
    st.markdown("---")
    if st.session_state.comparison_step == "template_list":
        st.subheader("📋 已上傳的比對範本")
        available_templates = get_comparison_templates()
        if available_templates:
            st.success(f"✅ 找到 {len(available_templates)} 個範本")
            for i, template in enumerate(available_templates):
                size_mb = f"{template['file_size'] / (1024 * 1024):.1f} MB" if template.get('file_size') else "未知"
                expander_title = f"📄 {template['name']} ({template.get('file_type', '未知')}, {size_mb})"
                with st.expander(expander_title):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**上傳日期**：{template.get('created_at', '未知')}")
                        st.write(f"**檔案類型**：{template.get('file_type', '未知')}")
                        st.write(f"**檔案大小**：{size_mb}")
                        st.write(f"**檔案名稱**：{template.get('filename', '未知')}")
                    with col2:
                        delete_button = st.button("🗑️ 刪除", key=f"del_template_{template['id']}", type="secondary")
                        if delete_button:
                            if delete_comparison_template(template['id']):
                                st.success(f"✅ 已刪除範本：{template['name']}")
                                st.rerun()
                            else:
                                st.error("刪除失敗，請重試")
                    with col3:
                        view_button = st.button("🔍 查看詳情", key=f"view_template_{template['id']}", type="secondary")
                        if view_button:
                            st.session_state.selected_template_id = template['id']
                            st.session_state.comparison_step = "template_detail"
                            st.rerun()
        else:
            # st.warning("⚠️ 沒有找到範本記錄") # 這行會和偵錯碼的 warning 混淆，暫時關閉
            st.info("目前沒有已上傳的比對範本。")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⬅️ 返回主選單", use_container_width=True):
                st.session_state.comparison_mode = None
                st.session_state.comparison_step = None
                st.rerun()
    else:
        st.info("目前沒有已上傳的比對範本。")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⬅️ 返回主選單", use_container_width=True):
                st.session_state.comparison_mode = None
                st.session_state.comparison_step = None
                st.rerun()

def show_comparison_selection():
    # ... (此函數內容保持不變) ...
    pass

def perform_document_comparison(template_file, target_file):
    # ... (此函數內容保持不變) ...
    pass

def initialize_comparison():
    if 'comparison_mode' not in st.session_state:
        st.session_state.comparison_mode = None
    if 'comparison_step' not in st.session_state:
        st.session_state.comparison_step = None
    if 'reference_file' not in st.session_state:
        st.session_state.reference_file = None
    if 'target_file' not in st.session_state:
        st.session_state.target_file = None

def show_document_comparison_main():
    initialize_comparison()
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ 返回首頁", key="back_to_home_comp"):
            st.session_state.comparison_mode = None
            st.session_state.comparison_step = None
            st.session_state.saved_template_id = None
            st.session_state.template_name = None
            st.session_state.page_selection = "🏠 系統首頁"
            st.rerun()
    if st.session_state.comparison_mode == "upload_template":
        show_template_upload()
    elif st.session_state.comparison_mode == "manage_templates":
        show_template_management()
    elif st.session_state.comparison_mode == "compare_templates":
        show_comparison_selection()
    else:
        show_document_comparison()
