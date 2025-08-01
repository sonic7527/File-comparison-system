import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 核心模組導入 ---
from core.database import (
    create_template_group, get_all_template_groups, get_template_files,
    get_field_definitions, update_field_definitions, delete_template_group,
    delete_template_file
)
from core.file_handler import (
    parse_excel_fields, save_uploaded_file, get_file_type, generate_document
)

# --- 常數設定 ---
UPLOAD_DIR = "uploads"
TEMPLATE_DIR = os.path.join(UPLOAD_DIR, "templates")
GENERATED_DIR = "generated_files"

# --- 初始化應用程式 ---
def initialize_app():
    """創建應用程式所需的目錄"""
    for path in [UPLOAD_DIR, TEMPLATE_DIR, GENERATED_DIR]:
        if not os.path.exists(path):
            os.makedirs(path)
    if 'dg_step' not in st.session_state:
        st.session_state.dg_step = 'main_view'
    if 'confirmation_data' not in st.session_state:
        st.session_state.confirmation_data = None

# --- UI 渲染函式 ---

def render_creation_tab():
    """渲染創建範本的 UI 介面"""
    st.subheader("📤 上傳檔案以建立新範本")
    with st.form("template_creation_form"):
        group_name = st.text_input("範本群組名稱", help="為這組範本命名，例如「2024年第一季合約」")
        source_excel = st.file_uploader("上傳欄位定義 Excel 檔", type=['xlsx'])
        template_files = st.file_uploader("上傳 Word/Excel 範本檔案", type=['docx', 'xlsx'], accept_multiple_files=True)
        submitted = st.form_submit_button("下一步：預覽與確認欄位")

        if submitted:
            if not all([group_name, source_excel, template_files]):
                st.warning("請填寫所有欄位並上傳所有必要的檔案。")
            else:
                excel_path = save_uploaded_file(source_excel, UPLOAD_DIR)
                parsed_fields = parse_excel_fields(excel_path)

                if not parsed_fields:
                    st.error("無法從 Excel 中解析出任何欄位，請檢查檔案格式是否正確。")
                    if os.path.exists(excel_path):
                        os.remove(excel_path)
                else:
                    st.session_state.confirmation_data = {
                        "action": "create",
                        "group_name": group_name,
                        "source_excel_path": excel_path,
                        "parsed_fields": parsed_fields,
                        "template_files": template_files
                    }
                    st.session_state.dg_step = 'confirm_view'
                    st.rerun()

def render_generation_tab():
    """渲染文件生成介面"""
    st.subheader("🚀 快速生成文件")
    template_groups = get_all_template_groups()
    if not template_groups:
        st.info("尚未建立任何範本群組，請先至「創建範本」頁籤建立新範本。")
        return

    group_options = {group['id']: group['name'] for group in template_groups}
    selected_group_id = st.selectbox("1. 選擇範本群組", options=list(group_options.keys()), format_func=lambda x: group_options[x])

    if selected_group_id:
        template_files = get_template_files(selected_group_id)
        if not template_files:
            st.warning("此範本群組中沒有可用的範本檔案。")
            return

        file_options = {f['id']: f['filename'] for f in template_files}
        selected_file_id = st.selectbox("2. 選擇範本檔案", options=list(file_options.keys()), format_func=lambda x: file_options[x])

        field_definitions = get_field_definitions(selected_group_id)
        st.markdown("---")
        st.markdown("##### 3. 填寫欄位內容")

        field_values = {}
        for i, field in enumerate(field_definitions):
            key = f"gen_{selected_group_id}_{i}"
            if 'dropdown_options' in field and field['dropdown_options']:
                options = field['dropdown_options']
                field_values[field['name']] = st.selectbox(field['name'], options=options, key=key, help=field.get('description', ''))
            else:
                field_values[field['name']] = st.text_input(field['name'], value=field.get('default_value', ''), key=key, help=field.get('description', ''))

        st.markdown("---")

        if st.button("✨ 生成文件", type="primary", use_container_width=True):
            selected_file_info = next((f for f in template_files if f['id'] == selected_file_id), None)
            if selected_file_info:
                template_path = selected_file_info['filepath']
                output_path = generate_document(template_path, field_values)

                if output_path and os.path.exists(output_path):
                    output_filename = os.path.basename(output_path)
                    st.success(f"文件 '{output_filename}' 已成功生成！")
                    with open(output_path, "rb") as f:
                        file_type = get_file_type(output_filename)
                        mime_type = f"application/vnd.openxmlformats-officedocument.{'wordprocessingml.document' if file_type == 'docx' else 'spreadsheetml.sheet'}"
                        st.download_button(
                            label=f"📥 下載 {output_filename}",
                            data=f,
                            file_name=output_filename,
                            mime=mime_type,
                            use_container_width=True
                        )
            else:
                st.error("選擇的範本檔案不存在，請重新整理。")

def render_management_tab():
    """渲染範本管理介面"""
    st.subheader("📚 管理現有範本")
    template_groups = get_all_template_groups()
    if not template_groups:
        st.info("目前沒有任何範本群組可供管理。")
        return

    for group in template_groups:
        with st.expander(f"**{group['name']}** (ID: {group['id']}) - 包含 {group['file_count']} 個檔案"):
            st.markdown(f"**來源 Excel:** `{os.path.basename(group['source_excel_path'])}`")
            st.markdown("---")
            st.markdown("###### 範本檔案清單:")
            template_files = get_template_files(group['id'])

            if not template_files:
                st.caption("此群組目前沒有範本檔案。")
            else:
                for f in template_files:
                    c1, c2 = st.columns([0.9, 0.1])
                    c1.text(f"📄 {f['filename']}")
                    if c2.button("❌", key=f"del_file_{f['id']}", help=f"刪除檔案: {f['filename']}"):
                        if delete_template_file(f['id']):
                            st.success(f"已成功刪除檔案: {f['filename']}")
                            st.rerun()
                        else:
                            st.error("刪除檔案時發生錯誤。")

            st.markdown("---")
            c1, c2 = st.columns(2)
            if c1.button("🔄 更新欄位", key=f"update_{group['id']}", use_container_width=True):
                excel_path = group['source_excel_path']
                if os.path.exists(excel_path):
                    st.session_state.confirmation_data = {
                        "action": "update",
                        "group_id": group['id'],
                        "group_name": group['name'],
                        "parsed_fields": parse_excel_fields(excel_path)
                    }
                    st.session_state.dg_step = 'confirm_view'
                    st.rerun()
                else:
                    st.error(f"錯誤：找不到來源 Excel 檔案 '{excel_path}'。")

            if c2.button("🗑️ 刪除整個群組", key=f"delete_{group['id']}", use_container_width=True):
                if delete_template_group(group['id']):
                    st.success(f"已成功刪除範本群組: {group['name']}")
                    st.rerun()
                else:
                    st.error("刪除群組時發生錯誤。")

def show_field_confirmation_view():
    """顯示欄位確認和修改的介面"""
    data = st.session_state.confirmation_data
    if not data:
        st.error("發生錯誤：找不到確認資料。返回主頁面...")
        st.session_state.dg_step = 'main_view'
        st.rerun()
        return

    action = data['action']
    title = "建立新範本" if action == 'create' else f"更新範本 '{data['group_name']}'"
    submit_label = "✅ 確認並建立" if action == 'create' else "✅ 確認並更新"

    st.header(f"🔍 請確認解析的欄位 - {title}")
    st.info("您可以在此處修改解析出的欄位名稱、預設值和描述。系統會根據這些定義來生成輸入介面。")

    with st.form("field_confirmation_form"):
        df = pd.DataFrame(data['parsed_fields'])
        df['dropdown_options'] = df['dropdown_options'].apply(lambda x: ','.join(x) if isinstance(x, list) else x)

        edited_df = st.data_editor(
            df,
            column_config={
                "name": st.column_config.TextColumn("欄位名稱", required=True),
                "default_value": "預設值",
                "description": "欄位描述 (提示)",
                "dropdown_options": "下拉選單選項 (用逗號分隔)",
            },
            num_rows="dynamic",
            use_container_width=True
        )

        c1, c2, _ = st.columns([1, 1, 4])
        if c1.form_submit_button(submit_label, type="primary"):
            final_fields = edited_df.to_dict('records')
            for field in final_fields:
                if isinstance(field.get('dropdown_options'), str) and field['dropdown_options']:
                    field['dropdown_options'] = [opt.strip() for opt in field['dropdown_options'].split(',')]
                else:
                    field['dropdown_options'] = []

            if action == 'create':
                handle_final_creation(data, final_fields)
            else:
                handle_final_update(data, final_fields)

            st.session_state.confirmation_data = None
            st.session_state.dg_step = 'main_view'
            st.rerun()

        if c2.form_submit_button("❌ 取消"):
            if action == 'create' and os.path.exists(data['source_excel_path']):
                os.remove(data['source_excel_path'])
            st.session_state.confirmation_data = None
            st.session_state.dg_step = 'main_view'
            st.rerun()

def handle_final_creation(data, final_fields):
    """處理最終的範本創建邏輯"""
    try:
        template_file_paths = [save_uploaded_file(f, TEMPLATE_DIR) for f in data['template_files']]
        create_template_group(
            name=data['group_name'],
            source_excel_path=data['source_excel_path'],
            field_definitions=final_fields,
            template_files=template_file_paths
        )
        st.success(f"範本群組 '{data['group_name']}' 已成功建立！")
    except Exception as e:
        st.error(f"建立範本時發生嚴重錯誤: {e}")
        if 'template_file_paths' in locals():
            for path in template_file_paths:
                if os.path.exists(path):
                    os.remove(path)
        if os.path.exists(data['source_excel_path']):
            os.remove(data['source_excel_path'])

def handle_final_update(data, final_fields):
    """處理最終的欄位更新邏輯"""
    try:
        if update_field_definitions(data['group_id'], final_fields):
            st.success(f"範本群組 '{data['group_name']}' 的欄位已成功更新！")
        else:
            st.error("更新欄位時發生錯誤。")
    except Exception as e:
        st.error(f"更新欄位時發生嚴重錯誤: {e}")

def show_document_generator():
    """根據 session state 決定顯示哪個視圖"""
    initialize_app()
    page_step = st.session_state.get('dg_step', 'main_view')
    if page_step == 'confirm_view':
        show_field_confirmation_view()
    else:
        tabs = st.tabs(["🚀 生成文件", "📁 創建範本", "📚 管理範本"])
        with tabs[0]:
            render_generation_tab()
        with tabs[1]:
            render_creation_tab()
        with tabs[2]:
            render_management_tab()
