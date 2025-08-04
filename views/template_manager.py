import streamlit as st
import os
import sqlite3
from datetime import datetime

# --- 核心模組導入 ---
from core.database import (
    get_all_template_groups, get_template_files, get_field_definitions,
    delete_template_group, delete_template_file, add_template_file
)
from utils.ui_components import show_turso_status_card

# --- 常數設定 ---
TEMPLATE_DIR = "uploads/templates"

def show_template_manager():
    """
    顯示範本管理主界面
    """
    # 返回按鈕
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ 返回首頁", key="back_to_home_tm"):
            st.session_state.page_selection = "🏠 系統首頁"
            st.rerun()
    
    st.title("⚙️ 智能文件生成範本管理")
    st.markdown("---")
    
    # 顯示整合的雲端連接狀態卡片
    show_turso_status_card()
    
    # 獲取範本群組
    try:
        from core.turso_database import TursoDatabase
        turso_db = TursoDatabase()
        
        if turso_db.is_cloud_mode():
            turso_db.create_tables()
            template_groups = turso_db.get_all_template_groups_cloud()
        else:
            template_groups = get_all_template_groups()
    except Exception as e:
        st.warning(f"雲端連接失敗，使用本地資料庫：{str(e)}")
        template_groups = get_all_template_groups()
    
    if not template_groups:
        st.info("尚未建立任何範本群組。")
        return
    
    # 顯示範本群組
    st.subheader("📋 範本群組列表")
    
    for group in template_groups:
        with st.expander(f"📁 {group['name']}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**建立時間**：{group.get('created_at', '未知')}")
                st.write(f"**來源檔案**：{group.get('source_excel_path', '未知')}")
                
                # 計算群組容量
                try:
                    if turso_db.is_cloud_mode():
                        template_files = turso_db.get_template_files_cloud(group['id'])
                    else:
                        template_files = get_template_files(group['id'])
                    
                    total_size = sum(f.get('file_size', 0) for f in template_files)
                    total_size_mb = total_size / (1024 * 1024)
                    st.write(f"**群組容量**：{total_size_mb:.2f} MB ({len(template_files)} 個檔案)")
                except Exception as e:
                    st.warning(f"無法獲取檔案資訊：{str(e)}")
            
            with col2:
                if st.button("🗑️ 刪除群組", key=f"delete_group_{group['id']}"):
                    try:
                        if turso_db.is_cloud_mode():
                            success = turso_db.delete_template_group_cloud(group['id'])
                        else:
                            success = delete_template_group(group['id'])
                        
                        if success:
                            st.success(f"✅ 群組 '{group['name']}' 已刪除")
                            st.rerun()
                        else:
                            st.error("❌ 刪除失敗")
                    except Exception as e:
                        st.error(f"刪除群組時發生錯誤：{str(e)}")
            
            with col3:
                if st.button("📄 查看檔案", key=f"view_files_{group['id']}"):
                    try:
                        if turso_db.is_cloud_mode():
                            files = turso_db.get_template_files_cloud(group['id'])
                        else:
                            files = get_template_files(group['id'])
                        
                        if files:
                            st.write("**範本檔案：**")
                            for file in files:
                                st.write(f"- {file['filename']} ({file['file_type']})")
                        else:
                            st.write("此群組中沒有範本檔案")
                    except Exception as e:
                        st.error(f"獲取檔案列表失敗：{str(e)}")
