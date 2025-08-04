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
from utils.ui_components import show_turso_status_card

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
    
    # 顯示上傳狀態
    if 'upload_status' in st.session_state:
        if st.session_state.upload_status.get('success'):
            st.success(st.session_state.upload_status['message'])
        else:
            st.error(st.session_state.upload_status['message'])
        # 清除狀態
        del st.session_state.upload_status
    
    with st.form("template_creation_form"):
        group_name = st.text_input("範本群組名稱", help="為這組範本命名，例如「2024年第一季合約」")
        source_excel = st.file_uploader("上傳欄位定義 Excel 檔", type=['xlsx'])
        template_files = st.file_uploader("上傳 Word/Excel 範本檔案", type=['docx', 'xlsx'], accept_multiple_files=True)
        submitted = st.form_submit_button("下一步：預覽與確認欄位")

        if submitted:
            st.info("🔄 開始處理上傳...")
            
            if not all([group_name, source_excel, template_files]):
                st.warning("請填寫所有欄位並上傳所有必要的檔案。")
            else:
                try:
                    st.info(f"📝 範本群組名稱：{group_name}")
                    st.info(f"📊 Excel 檔案：{source_excel.name if source_excel else '未上傳'}")
                    st.info(f"📄 範本檔案數量：{len(template_files) if template_files else 0}")
                    
                    # 保存 Excel 檔案
                    st.info("💾 正在保存 Excel 檔案...")
                    excel_path = save_uploaded_file(source_excel, UPLOAD_DIR)
                    st.success(f"✅ Excel 檔案已成功保存：{os.path.basename(excel_path)}")
                    
                    # 解析 Excel 欄位
                    st.info("🔍 正在解析 Excel 欄位...")
                    parsed_fields = parse_excel_fields(excel_path)

                    if not parsed_fields:
                        st.error("❌ 無法從 Excel 中解析出任何欄位")
                        st.info("請確認 Excel 檔案格式：第一欄為欄位名稱，第二欄為預設值，第三欄為說明")
                        if os.path.exists(excel_path):
                            os.remove(excel_path)
                    else:
                        st.success(f"✅ 成功解析 {len(parsed_fields)} 個欄位")
                        
                        # 保存範本檔案
                        saved_files = []
                        st.info(f"💾 正在保存 {len(template_files)} 個範本檔案...")
                        
                        for i, template_file in enumerate(template_files):
                            try:
                                st.info(f"正在處理第 {i+1} 個檔案：{template_file.name}")
                                file_path = save_uploaded_file(template_file, UPLOAD_DIR)
                                saved_files.append({
                                    'filename': template_file.name,
                                    'filepath': file_path,
                                    'file_type': get_file_type(file_path),
                                    'file_size': os.path.getsize(file_path)
                                })
                                st.success(f"✅ 範本檔案已成功保存：{template_file.name}")
                            except Exception as e:
                                st.error(f"❌ 保存範本檔案失敗：{template_file.name} - {str(e)}")
                        
                        if saved_files:
                            st.success(f"✅ 所有檔案上傳成功！共 {len(saved_files)} 個範本檔案")
                            
                            # 顯示詳細的檔案信息
                            st.info("📋 已保存的檔案：")
                            for i, file_info in enumerate(saved_files):
                                st.info(f"  {i+1}. {file_info['filename']} ({file_info['file_type']}, {file_info['file_size']} bytes)")
                            
                            # 先嘗試雲端上傳（預上傳）
                            cloud_upload_success = False
                            cloud_group_id = None
                            upload_errors = []
                            
                            st.info("☁️ 正在嘗試預上傳到雲端資料庫...")
                            try:
                                from core.turso_database import TursoDatabase
                                turso_db = TursoDatabase()
                                
                                if turso_db.is_cloud_mode():
                                    st.info("🔧 正在創建雲端表格...")
                                    turso_db.create_tables()
                                    st.info("🔧 正在預上傳範本群組到雲端...")
                                    
                                    # 詳細顯示上傳過程
                                    st.info(f"📝 群組名稱：{group_name}")
                                    st.info(f"📊 Excel檔案：{os.path.basename(excel_path)}")
                                    st.info(f"📄 範本檔案數量：{len(saved_files)}")
                                    
                                    for i, file_info in enumerate(saved_files):
                                        st.info(f"  📎 範本檔案 {i+1}：{file_info['filename']}")
                                    
                                    group_id = turso_db.create_template_group_cloud(
                                        name=group_name,
                                        source_excel_path=excel_path,
                                        field_definitions=parsed_fields,
                                        template_files=saved_files
                                    )
                                    
                                    if group_id > 0:
                                        cloud_upload_success = True
                                        cloud_group_id = group_id
                                        st.success(f"✅ 雲端預上傳成功！群組ID：{group_id}")
                                        
                                        # 驗證範本檔案是否真的上傳成功
                                        st.info("🔍 正在驗證範本檔案上傳狀態...")
                                        uploaded_files = turso_db.get_template_files_cloud(group_id)
                                        if uploaded_files:
                                            st.success(f"✅ 驗證成功！雲端共有 {len(uploaded_files)} 個範本檔案")
                                            for file_info in uploaded_files:
                                                st.info(f"  📎 {file_info['filename']}")
                                        else:
                                            st.warning("⚠️ 警告：雲端沒有找到範本檔案，可能上傳失敗")
                                            upload_errors.append("範本檔案上傳失敗")
                                    else:
                                        st.error(f"❌ 雲端預上傳失敗，返回的群組ID為：{group_id}")
                                        upload_errors.append(f"群組創建失敗，返回ID：{group_id}")
                                else:
                                    st.warning("⚠️ 雲端資料庫未配置，將在確認頁面處理")
                                    upload_errors.append("雲端資料庫未配置")
                            except Exception as e:
                                st.error(f"❌ 雲端預上傳失敗：{str(e)}")
                                import traceback
                                st.error(f"詳細錯誤：{traceback.format_exc()}")
                                upload_errors.append(f"雲端上傳異常：{str(e)}")
                                st.warning("將在確認頁面重新嘗試上傳")
                            
                            # 保存數據到session_state，供表單外部使用
                            st.session_state.upload_result = {
                                "group_name": group_name,
                                "excel_path": excel_path,
                                "parsed_fields": parsed_fields,
                                "saved_files": saved_files,
                                "cloud_upload_success": cloud_upload_success,
                                "cloud_group_id": cloud_group_id,
                                "upload_errors": upload_errors
                            }
                        else:
                            st.error("❌ 沒有成功保存任何範本檔案")
                            
                except Exception as e:
                    st.error(f"❌ 上傳過程中發生錯誤：{str(e)}")
                    st.info("請檢查檔案格式是否正確，或重新嘗試上傳")
    
    # 表單外部的按鈕處理
    if 'upload_result' in st.session_state:
        result = st.session_state.upload_result
        
        # 顯示下一步選項
        st.markdown("---")
        st.subheader("📋 下一步操作")
        
        if result['cloud_upload_success']:
            st.success("✅ 雲端上傳成功！您可以：")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 進入欄位確認頁面", key="enter_confirmation", type="primary"):
                    st.session_state.confirmation_data = {
                        "action": "create",
                        "group_name": result['group_name'],
                        "source_excel_path": result['excel_path'],
                        "parsed_fields": result['parsed_fields'],
                        "template_files": result['saved_files'],
                        "cloud_upload_success": result['cloud_upload_success'],
                        "cloud_group_id": result['cloud_group_id']
                    }
                    st.session_state.dg_step = 'confirm_view'
                    del st.session_state.upload_result
                    st.rerun()
            with col2:
                if st.button("📋 直接查看範本管理", key="view_templates"):
                    st.session_state.page_selection = "智能文件生成與管理"
                    del st.session_state.upload_result
                    st.rerun()
        else:
            st.warning("⚠️ 雲端上傳失敗，您可以：")
            if result['upload_errors']:
                st.error("錯誤詳情：")
                for error in result['upload_errors']:
                    st.error(f"  • {error}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 重新嘗試上傳", key="retry_upload", type="primary"):
                    st.session_state.confirmation_data = {
                        "action": "create",
                        "group_name": result['group_name'],
                        "source_excel_path": result['excel_path'],
                        "parsed_fields": result['parsed_fields'],
                        "template_files": result['saved_files'],
                        "cloud_upload_success": result['cloud_upload_success'],
                        "cloud_group_id": result['cloud_group_id']
                    }
                    st.session_state.dg_step = 'confirm_view'
                    del st.session_state.upload_result
                    st.rerun()
            with col2:
                if st.button("❌ 取消操作", key="cancel_upload"):
                    # 清理已保存的檔案
                    try:
                        if os.path.exists(result['excel_path']):
                            os.remove(result['excel_path'])
                        for file_info in result['saved_files']:
                            if os.path.exists(file_info['filepath']):
                                os.remove(file_info['filepath'])
                    except:
                        pass
                    del st.session_state.upload_result
                    st.rerun()

def render_generation_tab():
    """渲染文件生成介面"""
    st.subheader("🚀 快速生成文件")
    
    # 優先使用雲端資料庫
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
        st.info("尚未建立任何範本群組，請先至「創建範本」頁籤建立新範本。")
        return

    group_options = {group['id']: group['name'] for group in template_groups}
    selected_group_id = st.selectbox("1. 選擇範本群組", options=list(group_options.keys()), format_func=lambda x: group_options[x])

    if selected_group_id:
        # 獲取範本檔案
        try:
            if turso_db.is_cloud_mode():
                template_files = turso_db.get_template_files_cloud(selected_group_id)
            else:
                template_files = get_template_files(selected_group_id)
        except Exception as e:
            st.warning(f"獲取範本檔案失敗：{str(e)}")
            template_files = []

        if not template_files:
            st.warning("此範本群組中沒有可用的範本檔案。")
            return

        # 選擇範本檔案
        file_options = {file['id']: file['filename'] for file in template_files}
        selected_file_id = st.selectbox("2. 選擇範本檔案", options=list(file_options.keys()), format_func=lambda x: file_options[x])

        if selected_file_id:
            # 獲取欄位定義
            try:
                if turso_db.is_cloud_mode():
                    field_definitions = turso_db.get_field_definitions_cloud(selected_group_id)
                else:
                    field_definitions = get_field_definitions(selected_group_id)
            except Exception as e:
                st.warning(f"獲取欄位定義失敗：{str(e)}")
                field_definitions = []

            if not field_definitions:
                st.warning("此範本群組中沒有定義任何欄位。")
                return

            # 生成輸入表單
            st.subheader("3. 填寫欄位資料")
            with st.form("document_generation_form"):
                field_values = {}
                for field in field_definitions:
                    field_name = field['name']
                    field_desc = field.get('description', '')
                    default_value = field.get('default_value', '')
                    dropdown_options = field.get('dropdown_options', [])

                    if dropdown_options:
                        field_values[field_name] = st.selectbox(
                            f"{field_name} {f'({field_desc})' if field_desc else ''}",
                            options=dropdown_options,
                            index=dropdown_options.index(default_value) if default_value in dropdown_options else 0
                        )
                    else:
                        field_values[field_name] = st.text_input(
                            f"{field_name} {f'({field_desc})' if field_desc else ''}",
                            value=default_value
                        )

                submitted = st.form_submit_button("🚀 生成文件", type="primary")

                if submitted:
                    try:
                        # 獲取選中的檔案路徑
                        selected_file = next((f for f in template_files if f['id'] == selected_file_id), None)
                        if not selected_file:
                            st.error("找不到選中的範本檔案。")
                            return

                        file_path = selected_file['filepath']
                        if not os.path.exists(file_path):
                            st.error(f"範本檔案不存在：{file_path}")
                            return

                        # 生成文件
                        generated_path = generate_document(file_path, field_values)
                        
                        if generated_path:
                            # 保存生成的文件路徑到session_state
                            st.session_state.generated_file_path = generated_path
                            st.session_state.generated_file_name = os.path.basename(generated_path)
                            st.success(f"✅ 文件已成功生成！檔案名稱：{os.path.basename(generated_path)}")
                        else:
                            st.error("❌ 文件生成失敗")

                    except Exception as e:
                        st.error(f"生成文件時發生錯誤：{str(e)}")
            
            # 表單外部的下載按鈕
            if 'generated_file_path' in st.session_state and os.path.exists(st.session_state.generated_file_path):
                st.markdown("---")
                st.subheader("📥 下載生成的文件")
                
                with open(st.session_state.generated_file_path, "rb") as file:
                    st.download_button(
                        label="📥 下載生成的文件",
                        data=file.read(),
                        file_name=st.session_state.generated_file_name,
                        mime="application/octet-stream",
                        key="download_generated_file"
                    )
                
                # 清除session_state
                if st.button("🗑️ 清除生成記錄", key="clear_generated"):
                    del st.session_state.generated_file_path
                    del st.session_state.generated_file_name
                    st.rerun()

def render_management_tab():
    """渲染範本管理介面"""
    st.subheader("📋 範本管理")
    
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

    # 創建群組選項
    group_options = {}
    for group in template_groups:
        try:
            if turso_db.is_cloud_mode():
                files = turso_db.get_template_files_cloud(group['id'])
            else:
                files = get_template_files(group['id'])
            file_count = len(files) if files else 0
        except Exception as e:
            file_count = 0
        
        group_options[group['id']] = f"{group['name']} ({file_count} 個檔案)"
    
    # 群組選擇下拉式選單
    selected_group_id = st.selectbox(
        "選擇範本群組",
        options=list(group_options.keys()),
        format_func=lambda x: group_options[x],
        help="選擇要管理的範本群組"
    )
    
    if selected_group_id:
        # 獲取選中的群組信息
        selected_group = next((group for group in template_groups if group['id'] == selected_group_id), None)
        
        if selected_group:
            st.markdown("---")
            st.subheader(f"📁 {selected_group['name']}")
            
            # 顯示群組基本信息
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**群組名稱：** {selected_group['name']}")
                if 'source_excel_path' in selected_group:
                    st.write(f"**來源 Excel：** {os.path.basename(selected_group['source_excel_path'])}")
                st.write(f"**建立時間：** {selected_group.get('created_at', '未知')}")
            
            with col2:
                # 重新解析按鈕
                if st.button("🔄 重新解析基本資料", key=f"reparse_{selected_group_id}", type="primary"):
                    try:
                        excel_path = selected_group.get('source_excel_path')
                        if excel_path and os.path.exists(excel_path):
                            st.info("🔄 正在重新解析Excel欄位...")
                            parsed_fields = parse_excel_fields(excel_path)
                            
                            if parsed_fields:
                                st.success(f"✅ 重新解析成功！共 {len(parsed_fields)} 個欄位")
                                
                                # 設置確認資料
                                st.session_state.confirmation_data = {
                                    "action": "update",
                                    "group_id": selected_group['id'],
                                    "group_name": selected_group['name'],
                                    "source_excel_path": excel_path,
                                    "parsed_fields": parsed_fields,
                                    "template_files": turso_db.get_template_files_cloud(selected_group['id']) if turso_db.is_cloud_mode() else get_template_files(selected_group['id'])
                                }
                                st.session_state.dg_step = 'confirm_view'
                                st.rerun()
                            else:
                                st.error("❌ 無法從Excel中解析出任何欄位")
                        else:
                            st.error("❌ 找不到Excel檔案")
                    except Exception as e:
                        st.error(f"重新解析時發生錯誤：{str(e)}")
            
            # 顯示範本檔案
            st.markdown("### 📄 範本檔案")
            
            try:
                if turso_db.is_cloud_mode():
                    template_files = turso_db.get_template_files_cloud(selected_group_id)
                else:
                    template_files = get_template_files(selected_group_id)
                
                if template_files:
                    st.success(f"✅ 找到 {len(template_files)} 個範本檔案")
                    
                    # 顯示檔案列表
                    for i, file in enumerate(template_files, 1):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**{i}. {file['filename']}** ({file['file_type']})")
                            st.write(f"檔案大小：{file.get('file_size', 0)} bytes")
                        
                        with col2:
                            if st.button("🗑️ 刪除", key=f"delete_file_{file['id']}"):
                                try:
                                    if turso_db.is_cloud_mode():
                                        success = turso_db.delete_template_file_cloud(file['id'])
                                    else:
                                        success = delete_template_file(file['id'])
                                    
                                    if success:
                                        st.success(f"✅ 檔案 '{file['filename']}' 已刪除")
                                        st.rerun()
                                    else:
                                        st.error("❌ 刪除失敗")
                                except Exception as e:
                                    st.error(f"刪除檔案時發生錯誤：{str(e)}")
                        
                        with col3:
                            if st.button("📄 下載", key=f"download_file_{file['id']}"):
                                try:
                                    file_path = file['filepath']
                                    if os.path.exists(file_path):
                                        with open(file_path, "rb") as f:
                                            st.download_button(
                                                label=f"下載 {file['filename']}",
                                                data=f.read(),
                                                file_name=file['filename'],
                                                mime="application/octet-stream"
                                            )
                                    else:
                                        st.error("❌ 檔案不存在")
                                except Exception as e:
                                    st.error(f"下載檔案時發生錯誤：{str(e)}")
                    
                    st.markdown("---")
                    
                    # 新增範本檔案
                    st.subheader("📤 新增範本檔案")
                    uploaded_files = st.file_uploader(
                        "選擇要新增的範本檔案",
                        type=['docx', 'xlsx'],
                        accept_multiple_files=True,
                        key=f"add_files_{selected_group_id}"
                    )
                    
                    if uploaded_files:
                        if st.button("✅ 新增檔案到群組", key=f"add_files_btn_{selected_group_id}"):
                            try:
                                added_count = 0
                                for uploaded_file in uploaded_files:
                                    # 保存檔案
                                    file_path = save_uploaded_file(uploaded_file, UPLOAD_DIR)
                                    
                                    # 添加到資料庫
                                    file_info = {
                                        'filename': uploaded_file.name,
                                        'filepath': file_path,
                                        'file_type': get_file_type(file_path),
                                        'file_size': os.path.getsize(file_path)
                                    }
                                    
                                    if turso_db.is_cloud_mode():
                                        success = turso_db.add_template_file_cloud(selected_group_id, file_info)
                                    else:
                                        success = add_template_file(selected_group_id, file_info)
                                    
                                    if success:
                                        st.success(f"✅ 檔案 '{uploaded_file.name}' 已新增到群組")
                                        added_count += 1
                                    else:
                                        st.error(f"❌ 新增檔案 '{uploaded_file.name}' 失敗")
                                
                                if added_count > 0:
                                    st.success(f"✅ 成功新增 {added_count} 個檔案")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"新增檔案時發生錯誤：{str(e)}")
                
                else:
                    st.warning("⚠️ 此群組中沒有範本檔案")
                    
                    # 新增第一個範本檔案
                    st.subheader("📤 新增第一個範本檔案")
                    uploaded_files = st.file_uploader(
                        "選擇要新增的範本檔案",
                        type=['docx', 'xlsx'],
                        accept_multiple_files=True,
                        key=f"add_first_files_{selected_group_id}"
                    )
                    
                    if uploaded_files:
                        if st.button("✅ 新增檔案到群組", key=f"add_first_files_btn_{selected_group_id}"):
                            try:
                                added_count = 0
                                for uploaded_file in uploaded_files:
                                    # 保存檔案
                                    file_path = save_uploaded_file(uploaded_file, UPLOAD_DIR)
                                    
                                    # 添加到資料庫
                                    file_info = {
                                        'filename': uploaded_file.name,
                                        'filepath': file_path,
                                        'file_type': get_file_type(file_path),
                                        'file_size': os.path.getsize(file_path)
                                    }
                                    
                                    if turso_db.is_cloud_mode():
                                        success = turso_db.add_template_file_cloud(selected_group_id, file_info)
                                    else:
                                        success = add_template_file(selected_group_id, file_info)
                                    
                                    if success:
                                        st.success(f"✅ 檔案 '{uploaded_file.name}' 已新增到群組")
                                        added_count += 1
                                    else:
                                        st.error(f"❌ 新增檔案 '{uploaded_file.name}' 失敗")
                                
                                if added_count > 0:
                                    st.success(f"✅ 成功新增 {added_count} 個檔案")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"新增檔案時發生錯誤：{str(e)}")
                
            except Exception as e:
                st.error(f"獲取範本檔案時發生錯誤：{str(e)}")
            
            # 刪除群組按鈕
            st.markdown("---")
            if st.button("🗑️ 刪除整個群組", key=f"delete_group_{selected_group_id}", type="secondary"):
                try:
                    if turso_db.is_cloud_mode():
                        success = turso_db.delete_template_group_cloud(selected_group_id)
                    else:
                        success = delete_template_group(selected_group_id)
                    
                    if success:
                        st.success(f"✅ 群組 '{selected_group['name']}' 已刪除")
                        st.rerun()
                    else:
                        st.error("❌ 刪除失敗")
                except Exception as e:
                    st.error(f"刪除群組時發生錯誤：{str(e)}")

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
    
    # 顯示預上傳狀態
    if action == 'create' and 'cloud_upload_success' in data:
        if data['cloud_upload_success']:
            st.success(f"✅ 雲端預上傳成功！群組ID：{data['cloud_group_id']}")
            st.info("📋 確認欄位後，範本將正式保存到雲端資料庫")
        else:
            st.warning("⚠️ 雲端預上傳失敗，確認欄位後將重新嘗試上傳")

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
                st.info("🔄 正在處理範本創建...")
                
                # 如果預上傳成功，直接使用預上傳的結果
                if data.get('cloud_upload_success') and data.get('cloud_group_id'):
                    st.success(f"✅ 範本群組 '{data['group_name']}' 已成功建立！群組ID：{data['cloud_group_id']}")
                    st.info("📋 您現在可以在「範本管理」頁面查看新建立的範本群組。")
                    # 清理本地檔案
                    try:
                        if os.path.exists(data['source_excel_path']):
                            os.remove(data['source_excel_path'])
                        for file_info in data['template_files']:
                            if os.path.exists(file_info['filepath']):
                                os.remove(file_info['filepath'])
                    except:
                        pass
                    # 延遲重新載入，讓用戶看到成功訊息
                    import time
                    time.sleep(2)
                    st.session_state.confirmation_data = None
                    st.session_state.dg_step = 'main_view'
                    st.rerun()
                else:
                    # 如果預上傳失敗，重新嘗試上傳
                    success = handle_final_creation(data, final_fields)
                    if success:
                        st.success(f"✅ 範本群組 '{data['group_name']}' 已成功建立！")
                        st.info("📋 您現在可以在「範本管理」頁面查看新建立的範本群組。")
                        # 延遲重新載入，讓用戶看到成功訊息
                        import time
                        time.sleep(2)
                        st.session_state.confirmation_data = None
                        st.session_state.dg_step = 'main_view'
                        st.rerun()
                    else:
                        st.error("❌ 範本建立失敗")
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
        # 只使用雲端資料庫
        try:
            from core.turso_database import TursoDatabase
            turso_db = TursoDatabase()
            
            if not turso_db.is_cloud_mode():
                st.error("❌ 雲端資料庫未配置，無法保存範本")
                st.error("請確認 .streamlit/secrets.toml 檔案中有正確的 Turso 配置")
                return False
            
            # 雲端模式：使用已經保存的檔案
            st.info("☁️ 正在保存到雲端資料庫...")
            st.info(f"🔧 調試信息：群組名稱 = {data['group_name']}")
            st.info(f"🔧 調試信息：Excel路徑 = {data['source_excel_path']}")
            st.info(f"🔧 調試信息：範本檔案數量 = {len(data['template_files'])}")
            
            # 使用已經保存的檔案資訊
            template_files_info = data['template_files']
            
            # 創建到雲端
            try:
                st.info("🔧 正在創建雲端表格...")
                turso_db.create_tables()
                st.info("🔧 正在創建範本群組到雲端...")
                group_id = turso_db.create_template_group_cloud(
                    name=data['group_name'],
                    source_excel_path=data['source_excel_path'],
                    field_definitions=final_fields,
                    template_files=template_files_info
                )
                
                if group_id > 0:
                    st.success(f"✅ 範本群組已成功保存到雲端！群組ID：{group_id}")
                    return True
                else:
                    st.error(f"❌ 雲端創建範本群組失敗，返回的群組ID為：{group_id}")
                    return False
            except Exception as e:
                st.error(f"❌ 雲端創建範本群組錯誤：{str(e)}")
                import traceback
                st.error(f"詳細錯誤：{traceback.format_exc()}")
                return False
        except Exception as e:
            st.error(f"❌ 雲端連接失敗：{str(e)}")
            return False
    except Exception as e:
        st.error(f"❌ 建立範本時發生嚴重錯誤: {e}")
        # 清理已保存的檔案
        try:
            if os.path.exists(data['source_excel_path']):
                os.remove(data['source_excel_path'])
            for file_info in data['template_files']:
                if os.path.exists(file_info['filepath']):
                    os.remove(file_info['filepath'])
        except:
            pass
        return False

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
    """
    顯示文件生成器主界面
    """
    # 返回按鈕
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ 返回首頁", key="back_to_home_dg"):
            st.session_state.page_selection = "🏠 系統首頁"
            st.rerun()
    
    st.title("📝 智能文件生成與管理")
    st.markdown("---")
    
    # 顯示整合的雲端連接狀態卡片
    show_turso_status_card()
    
    # 初始化應用程式
    initialize_app()
    
    # 檢查是否需要顯示確認視圖
    if st.session_state.get('dg_step') == 'confirm_view':
        show_field_confirmation_view()
        return
    
    # 創建分頁
    tab1, tab2, tab3 = st.tabs(["🚀 創建範本", "📄 生成文件", "⚙️ 範本管理"])
    
    with tab1:
        render_creation_tab()
    
    with tab2:
        render_generation_tab()
    
    with tab3:
        render_management_tab()
