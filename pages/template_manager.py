import streamlit as st
import os
from core.database import get_all_template_groups, get_template_files, delete_template_group, delete_template_file, update_template_group_fields

def show_template_manager():
    """範本管理主頁面"""
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("📚 範本管理")

    groups = get_all_template_groups()

    if not groups:
        st.info("目前沒有可用的範本群組。")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    for group in groups:
        with st.expander(f"📁 {group['name']} ({group['file_count']}個檔案)", expanded=True):
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                st.write(f"**來源Excel:** `{os.path.basename(group['excel_path'])}`")
                template_files = get_template_files(group['id'])
                if not template_files:
                    st.write("此群組尚無範本檔案。")
                else:
                    for f in template_files:
                        sub_col1, sub_col2 = st.columns([4, 1])
                        sub_col1.button(f"{f['filename']} ({f['file_type']})", key=f"file_{f['id']}", disabled=True)
                        if sub_col2.button("❌", key=f"del_file_{f['id']}", help=f"刪除檔案: {f['filename']}"):
                            if delete_template_file(f['id']):
                                st.success(f"已刪除檔案: {f['filename']}")
                                st.experimental_rerun()
                            else:
                                st.error("刪除檔案失敗")
            
            with col2:
                if st.button("🔄 更新欄位", key=f"reparse_{group['id']}", help="使用原始Excel重新解析欄位"):
                    new_fields = update_template_group_fields(group['id'])
                    if new_fields is not None:
                        st.success(f"已成功更新 {len(new_fields)} 個欄位！")
                    else:
                        st.error("更新欄位失敗，請檢查原始Excel檔案是否存在。")

            with col3:
                if st.button("🗑️ 刪除群組", key=f"delete_group_{group['id']}", type="secondary"):
                    if delete_template_group(group['id']):
                        st.success(f"已刪除範本群組: {group['name']}")
                        st.experimental_rerun()
                    else:
                        st.error("刪除群組失敗")
    
    st.markdown('</div>', unsafe_allow_html=True)
