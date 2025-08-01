import streamlit as st
import os
from core.database import (
    create_template_group, add_template_file, get_all_template_groups,
    get_template_files, get_field_definitions, delete_template_group,
    delete_template_file, update_field_definitions
)
from core.file_handler import (
    parse_excel_fields, get_file_type, save_uploaded_file, generate_document
)

# --- 主路由器：根據頁面步驟顯示不同內容 ---
def show_document_generator():
    """此頁面的主路由器"""
    page_step = st.session_state.get('dg_step', 'main_view')

    if page_step == 'confirm_view':
        show_field_confirmation_view()
    else:
        show_main_view()

# --- 主視圖：包含三個分頁 ---
def show_main_view():
    st.title("📝 智能文件生成與管理")
    tabs = st.tabs(["🚀 生成文件", "📁 創建範本", "📚 管理範本"])
    with tabs[0]:
        render_generation_tab()
    with tabs[1]:
        render_creation_tab()
    with tabs[2]:
        render_management_tab()

# --- 創建範本 Tab ---
def render_creation_tab():
    with st.form("template_creation_form"):
        st.markdown("##### 步驟 1: 上傳基本資料Excel檔")
        excel_file = st.file_uploader("選擇Excel", type=['xlsx', 'xls'], help="第一欄:欄位名, 第二欄:範例值, 第三欄:描述", key="creator_excel")
        
        st.markdown("##### 步驟 2: 上傳範本檔案 (可多選)")
        template_files = st.file_uploader("選擇Word/Excel範本", type=['docx', 'xlsx'], accept_multiple_files=True, key="creator_templates")
        
        st.markdown("##### 步驟 3: 命名範本群組")
        template_name = st.text_input("範本群組名稱", placeholder="例如：公司合約範本")
        
        if st.form_submit_button("📋 解析欄位", type="primary"):
            if excel_file and template_files and template_name:
                excel_path = save_uploaded_file(excel_file, "data/excel")
                fields = parse_excel_fields(excel_path)
                if fields:
                    st.session_state.confirmation_data = {
                        'is_update': False,
                        'name': template_name,
                        'excel_path': excel_path,
                        'template_files': template_files,
                        'fields': fields
                    }
                    st.session_state.dg_step = 'confirm_view'
                    st.experimental_rerun()
                else:
                    st.error("無法從Excel解析欄位，請檢查檔案格式")
            else:
                st.error("請填寫所有欄位並上傳檔案")

# --- 欄位確認視圖 (新建與更新共用) ---
def show_field_confirmation_view():
    conf_data = st.session_state.get('confirmation_data', {})
    is_update = conf_data.get('is_update', False)
    
    st.subheader("📋 更新並確認欄位定義" if is_update else "📋 確認新建欄位定義")
    st.info("請確認欄位是否正確，可在此即時修正。")

    with st.form("field_confirmation_form"):
        fields = conf_data.get('fields', [])
        for i, field in enumerate(fields):
            with st.expander(f"欄位 {i+1}: {field.get('name', '')}", expanded=True):
                if field.get('dropdown_options'):
                    st.write(f"**{field.get('name', '')}** (下拉選單)")
                    current_value = field.get('value', '')
                    options = field['dropdown_options']
                    index = options.index(current_value) if current_value in options else 0
                    field['value'] = st.selectbox("選擇一個選項", options, index=index, key=f"dd_{i}")
                else:
                    field['name'] = st.text_input("欄位名稱", field.get('name', ''), key=f"name_{i}")
                    field['value'] = st.text_input("範例值", field.get('value', ''), key=f"value_{i}")

                field['description'] = st.text_area("欄位描述", field.get('description', ''), key=f"desc_{i}", height=100)
        
        submit_label = "✅ 確認並更新" if is_update else "✅ 確認並建立"
        c1, c2 = st.columns(2)
        if c1.form_submit_button(submit_label, type="primary"):
            if is_update:
                update_field_definitions(conf_data['group_id'], fields)
                st.success(f"範本群組 「{conf_data['name']}」 的欄位已成功更新！")
            else:
                group_id = create_template_group(conf_data['name'], conf_data['excel_path'], fields)
                for f in conf_data['template_files']:
                    path = save_uploaded_file(f, "data/templates")
                    file_type = get_file_type(f.name)
                    add_template_file(group_id, f.name, path, file_type)
                st.success(f"範本群組「{conf_data['name']}」建立成功！")
            
            del st.session_state.confirmation_data
            st.session_state.dg_step = 'main_view'
            st.experimental_rerun()

        if c2.form_submit_button("❌ 取消"):
            del st.session_state.confirmation_data
            st.session_state.dg_step = 'main_view'
            st.experimental_rerun()

# --- 文件生成 Tab ---
def render_generation_tab():
    groups = get_all_template_groups()
    if not groups:
        st.warning("目前沒有可用的範本，請先創建。")
        return

    group_options = {f"{g['name']} ({g.get('file_count', 0)}個檔案)": g['id'] for g in groups}
    selected_group_name = st.selectbox("步驟1: 選擇範本群組", list(group_options.keys()))
    
    if not selected_group_name: return
    selected_group_id = group_options[selected_group_name]
    
    template_files = get_template_files(selected_group_id)
    if not template_files:
        st.warning("此群組沒有範本檔案。")
        return
        
    file_options = {f"{f['filename']} ({f['file_type']})": f for f in template_files}
    selected_file_name = st.selectbox("步驟2: 選擇範本檔案", list(file_options.keys()))
    
    if not selected_file_name: return
    selected_file = file_options[selected_file_name]

    st.markdown("---")
    st.markdown("##### 步驟3: 填寫欄位值")
    fields = get_field_definitions(selected_group_id)
    if not fields:
        st.warning("此範本群組沒有定義欄位。")
        return

    field_values = {}
    for i, field in enumerate(fields):
        label = field.get('description') or field['name']
        if field.get('dropdown_options'):
            options = field['dropdown_options']
            current_value = field.get('value', '')
            index = options.index(current_value) if current_value in options else 0
            field_values[field['name']] = st.selectbox(label, options, index=index, key=f"gen_dd_{selected_group_id}_{i}")
        else:
            field_values[field['name']] = st.text_input(label, value=field.get('value', ''), key=f"gen_{selected_group_id}_{i}")

    if st.button("🎯 生成文件", type="primary"):
        with st.spinner("正在生成文件..."):
            output_path = generate_document(selected_file['filepath'], field_values)
        if output_path:
            st.success("文件生成成功！")
            with open(output_path, "rb") as file_data:
                st.download_button("📥 下載文件", file_data, os.path.basename(output_path))
        else:
            st.error("文件生成失敗。")

# --- 範本管理 Tab ---
def render_management_tab():
    st.subheader("📚 現有範本群組管理")
    groups = get_all_template_groups()
    if not groups:
        st.info("目前沒有可用的範本群組。")
        return

    for group in groups:
        with st.expander(f"📁 {group['name']} ({group.get('file_count', 0)}個檔案)", expanded=True):
            template_files = get_template_files(group['id'])
            if not template_files:
                st.write("此群組尚無範本檔案。")
            else:
                for f in template_files:
                    c1, c2 = st.columns([5, 1])
                    c1.button