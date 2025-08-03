import streamlit as st
import os
from core.database import get_all_template_groups, get_template_files, delete_template_group, delete_template_file, update_template_group_fields
from core.file_handler import save_uploaded_file

def show_template_manager():
    """範本管理主頁面"""
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("📚 範本管理")

    groups = get_all_template_groups()

    if not groups:
        st.info("目前沒有可用的範本群組。")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 如果有多個群組，讓用戶選擇
    if len(groups) > 1:
        st.subheader("📋 選擇要管理的範本群組")
        
        # 創建群組選項
        group_options = {group['id']: f"{group['name']} ({group['file_count']}個檔案)" for group in groups}
        selected_group_id = st.selectbox(
            "選擇範本群組",
            options=list(group_options.keys()),
            format_func=lambda x: group_options[x],
            key="template_group_selector"
        )
        
        # 顯示選中群組的容量統計
        selected_group = next((g for g in groups if g['id'] == selected_group_id), None)
        if selected_group:
            template_files = get_template_files(selected_group_id)
            total_size = 0
            for file_info in template_files:
                try:
                    if os.path.exists(file_info['filepath']):
                        file_size = os.path.getsize(file_info['filepath'])
                        total_size += file_size
                except:
                    pass
            
            st.info(f"📊 **群組容量**: {round(total_size / (1024 * 1024), 2)} MB")
            st.markdown("---")
    else:
        # 只有一個群組時，直接使用
        selected_group_id = groups[0]['id']
        selected_group = groups[0]

    # 顯示選中群組的詳細信息
    if selected_group:
        st.subheader(f"📁 {selected_group['name']}")
        
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            # 顯示基本資料Excel檔案
            excel_filename = os.path.basename(selected_group['source_excel_path'])
            st.write(f"**基本資料Excel:** `{excel_filename}`")
            
            # 顯示範本檔案
            template_files = get_template_files(selected_group_id)
            if not template_files:
                st.write("此群組尚無範本檔案。")
            else:
                st.write("**範本檔案:**")
                for f in template_files:
                    sub_col1, sub_col2 = st.columns([4, 1])
                    # 顯示檔案大小
                    try:
                        if os.path.exists(f['filepath']):
                            file_size = os.path.getsize(f['filepath'])
                            file_size_mb = round(file_size / (1024 * 1024), 2)
                            sub_col1.button(f"{f['filename']} ({f['file_type']}) - {file_size_mb}MB", key=f"file_{f['id']}", disabled=True)
                        else:
                            sub_col1.button(f"{f['filename']} ({f['file_type']}) - 檔案不存在", key=f"file_{f['id']}", disabled=True)
                    except:
                        sub_col1.button(f"{f['filename']} ({f['file_type']}) - 容量計算失敗", key=f"file_{f['id']}", disabled=True)
                    
                    if sub_col2.button("❌", key=f"del_file_{f['id']}", help=f"刪除檔案: {f['filename']}"):
                        if delete_template_file(f['id']):
                            st.success(f"已刪除檔案: {f['filename']}")
                            st.rerun()
                        else:
                            st.error("刪除檔案失敗")
            
            # 新增範本檔案功能
            st.markdown("---")
            st.write("**新增範本檔案:**")
            new_template = st.file_uploader(
                "上傳新的範本檔案",
                type=['docx', 'xlsx'],
                key=f"upload_new_template_{selected_group_id}",
                help="支援 Word (.docx) 和 Excel (.xlsx) 格式"
            )
            
            if new_template:
                if st.button("📤 新增範本", key=f"add_template_{selected_group_id}"):
                    try:
                        # 保存新檔案
                        template_dir = "uploads/templates"
                        os.makedirs(template_dir, exist_ok=True)
                        template_path = save_uploaded_file(new_template, template_dir)
                        
                        # 添加到資料庫
                        from core.database import get_db_connection
                        with get_db_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO template_files (group_id, filename, filepath, file_type) VALUES (?, ?, ?, ?)",
                                (selected_group_id, new_template.name, template_path, new_template.name.split('.')[-1].upper())
                            )
                            conn.commit()
                        
                        st.success(f"已成功新增範本檔案: {new_template.name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"新增範本失敗: {str(e)}")
        
        with col2:
            if st.button("🔄 重新解析", key=f"reparse_{selected_group_id}", help="使用基本資料Excel重新解析欄位"):
                # 重新解析該群組的Excel欄位
                try:
                    excel_file = selected_group.get('source_excel_path')
                    
                    if excel_file and os.path.exists(excel_file):
                        # 重新解析Excel欄位
                        from core.file_handler import parse_excel_fields
                        parsed_fields = parse_excel_fields(excel_file)
                        
                        if parsed_fields:
                            # 顯示重新解析的欄位供確認
                            st.session_state.confirmation_data = {
                                "action": "update",
                                "group_id": selected_group_id,
                                "group_name": selected_group['name'],
                                "source_excel_path": excel_file,
                                "parsed_fields": parsed_fields,
                                "template_files": []  # 不需要重新上傳範本檔案
                            }
                            st.session_state.dg_step = 'confirm_view'
                            st.rerun()
                        else:
                            st.error("無法從Excel中解析出任何欄位，請檢查檔案格式。")
                    else:
                        st.error("找不到該群組的Excel檔案，無法重新解析。")
                except Exception as e:
                    st.error(f"重新解析失敗：{str(e)}")

        with col3:
            if st.button("🗑️ 刪除群組", key=f"delete_group_{selected_group_id}", type="secondary"):
                if delete_template_group(selected_group_id):
                    st.success(f"已刪除範本群組: {selected_group['name']}")
                    st.rerun()
                else:
                    st.error("刪除群組失敗")
    
    st.markdown('</div>', unsafe_allow_html=True)
