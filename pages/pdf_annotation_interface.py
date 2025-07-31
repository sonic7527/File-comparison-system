# 檔名: pages/pdf_annotation_interface.py
# (已加入刪除單筆標記功能的最終版本)

import streamlit as st
from PIL import Image
import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pdf_annotation_system import PDFAnnotationSystem

# 嘗試導入 streamlit_drawable_canvas，如果失敗則提供備用方案
try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False
    st.warning("⚠️ streamlit_drawable_canvas 套件未安裝，請執行：pip install streamlit-drawable-canvas")

def pdf_annotation_interface():
    st.markdown("## 🎨 PDF 變數標記系統")
    if 'annotation_system' not in st.session_state:
        st.session_state.annotation_system = PDFAnnotationSystem()
    system = st.session_state.annotation_system
    
    tab1, tab2, tab3, tab4 = st.tabs(["📤 上傳範本", "🎨 標記變數", "📊 變數資料庫", "🔍 範本管理"])
    with tab1: upload_template_tab(system)
    with tab2: annotation_tab(system)
    with tab3: variable_database_tab(system)
    with tab4: template_management_tab(system)

def upload_template_tab(system: PDFAnnotationSystem):
    st.markdown("### 📤 上傳新的 PDF 範本")
    with st.form("upload_form", clear_on_submit=True):
        template_name = st.text_input("範本名稱", placeholder="例如：保險申請書")
        template_description = st.text_input("範本描述", placeholder="範本用途說明")
        uploaded_file = st.file_uploader("選擇 PDF 檔案", type=['pdf'])
        submitted = st.form_submit_button("🚀 處理並儲存範本")
        if submitted and template_name and uploaded_file:
            with st.spinner("正在處理 PDF 檔案..."):
                images = system.convert_pdf_to_images(uploaded_file)
                if images:
                    if system.save_template(template_name, template_description, uploaded_file, images) != -1:
                        st.success(f"✅ 範本 '{template_name}' 儲存成功！")
                else:
                    st.error("❌ PDF 處理失敗。")
        elif submitted:
            st.warning("⚠️ 請務必填寫範本名稱並上傳檔案。")

# --- 【修改點在這裡】 ---
def annotation_tab(system: PDFAnnotationSystem):
    st.markdown("### 🎨 變數標記工具")
    templates = system.get_templates_list()
    if not templates:
        st.info("📝 請先到『上傳範本』分頁建立範本。")
        return
    
    template_names = [t.get('name', f"無效範本ID_{t.get('id', 'N/A')}") for t in templates]
    selected_template_name = st.selectbox("選擇要標記的範本", template_names)
    
    if selected_template_name:
        template_info = next((t for t in templates if t.get('name') == selected_template_name), None)
        if not template_info: 
            st.error("無法載入選擇的範本，可能資料有誤。")
            return

        # 頁面選擇和類型設定
        col_page, col_type = st.columns([2, 1])
        with col_page:
            page_num = st.slider("選擇頁面", 1, template_info.get('total_pages', 1), 1)
        
        with col_type:
            current_page_type, current_note = system.get_page_info(template_info['id'], page_num)
            page_type = st.selectbox(
                "頁面類型",
                ["變數頁面", "參考資料"],
                index=0 if current_page_type == "變數頁面" else 1,
                key=f"page_type_{template_info['id']}_{page_num}",
                help="變數頁面：需要精確比對變數；參考資料：只需相似度比對"
            )
        
        # 備註欄位（只有參考資料才顯示）
        page_note = ""
        if page_type == "參考資料":
            st.markdown("#### 📝 頁面備註")
            page_note = st.text_input(
                "備註說明",
                value=current_note,
                placeholder="例如：INV廠商型錄、技師證照、產品規格書...",
                key=f"page_note_{template_info['id']}_{page_num}",
                help="描述此參考資料頁面的內容"
            )
        
        # 檢查是否需要更新頁面資訊
        if page_type != current_page_type or (page_type == "參考資料" and page_note != current_note):
            if st.button("💾 更新頁面設定", key=f"update_page_{template_info['id']}_{page_num}"):
                if system.set_page_type(template_info['id'], page_num, page_type, page_note):
                    st.success("✅ 頁面設定已更新")
                    st.rerun()
        
        # 顯示頁面類型狀態
        if page_type == "變數頁面":
            st.info("📝 **變數頁面** - 此頁面將進行精確的變數比對")
        else:
            note_display = f" - {page_note}" if page_note else ""
            st.info(f"📄 **參考資料頁面**{note_display} - 此頁面只進行相似度比對，不需要標記變數")
        
        page_image = system.load_template_page(template_info['id'], page_num)
        
        if page_image:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"#### 📄 第 {page_num} 頁")
                
                if CANVAS_AVAILABLE:
                    # 使用canvas進行標記
                    canvas_width = 800
                    scale = canvas_width / page_image.width
                    canvas_height = int(page_image.height * scale)
                    
                    try:
                        canvas_result = st_canvas(
                            fill_color="rgba(255, 0, 0, 0.3)", stroke_width=2, stroke_color="#FF0000",
                            background_image=page_image, update_streamlit=True,
                            width=canvas_width, height=canvas_height, drawing_mode="rect",
                            key=f"canvas_{template_info['id']}_{page_num}"
                        )
                    except Exception as e:
                        st.error(f"Canvas載入錯誤：{str(e)}")
                        st.info("💡 請嘗試重新安裝：pip install streamlit-drawable-canvas==0.9.3")
                        canvas_result = None
                else:
                    # 備用方案：顯示圖片並使用座標輸入
                    st.image(page_image, width=800, caption=f"第 {page_num} 頁")
                    st.warning("⚠️ 無法使用視覺化標記工具，請手動輸入座標")
                    canvas_result = None
            
            with col2:
                st.markdown("#### ⚙️ 變數設定")
                
                # 檢查是否可以使用canvas
                if CANVAS_AVAILABLE and canvas_result and canvas_result.json_data and canvas_result.json_data["objects"]:
                    # 使用canvas的標記結果
                    with st.form(key=f"annotation_form_{template_info['id']}_{page_num}"):
                        variable_name = st.text_input("變數名稱", placeholder="例如：客戶姓名")
                        variable_type = st.selectbox("變數類型", ["文字", "數字", "日期", "地址", "其他"])
                        sample_value = st.text_input("範例值 (可選)")
                        submitted = st.form_submit_button("💾 儲存此標記")
                        if submitted and variable_name:
                            last_rect = canvas_result.json_data["objects"][-1]
                            coords = (last_rect["left"]/scale, last_rect["top"]/scale, 
                                      (last_rect["left"]+last_rect["width"])/scale, 
                                      (last_rect["top"]+last_rect["height"])/scale)
                            if system.save_annotation(template_info['id'], page_num, variable_name, variable_type, coords, sample_value):
                                st.success(f"✅ 成功儲存變數 '{variable_name}'！")
                                st.rerun()
                
                elif not CANVAS_AVAILABLE:
                    # 備用方案：手動輸入座標
                    st.info("📝 手動座標輸入模式")
                    with st.form(key=f"manual_annotation_form_{template_info['id']}_{page_num}"):
                        variable_name = st.text_input("變數名稱", placeholder="例如：客戶姓名")
                        variable_type = st.selectbox("變數類型", ["文字", "數字", "日期", "地址", "其他"])
                        sample_value = st.text_input("範例值 (可選)")
                        
                        st.markdown("**座標位置 (像素):**")
                        col_x, col_y = st.columns(2)
                        with col_x:
                            x_start = st.number_input("X起始", min_value=0, value=0)
                            x_end = st.number_input("X結束", min_value=0, value=100)
                        with col_y:
                            y_start = st.number_input("Y起始", min_value=0, value=0)
                            y_end = st.number_input("Y結束", min_value=0, value=30)
                        
                        submitted = st.form_submit_button("💾 儲存此標記")
                        if submitted and variable_name:
                            coords = (x_start, y_start, x_end, y_end)
                            if system.save_annotation(template_info['id'], page_num, variable_name, variable_type, coords, sample_value):
                                st.success(f"✅ 成功儲存變數 '{variable_name}'！")
                                st.rerun()
                
                else:
                    if CANVAS_AVAILABLE:
                        st.info("🎯 請在左側圖片上拖拉一個矩形區域來定義變數。")
                    else:
                        st.info("📝 請填寫上方表單來手動定義變數位置。")

            st.markdown("---")
            st.markdown("#### 📋 本頁現有標記")
            annotations = system.get_template_annotations(template_info['id'], page_num)
            
            # 初始化編輯狀態
            if 'editing_annotation' not in st.session_state:
                st.session_state.editing_annotation = None
            
            if annotations:
                for ann in annotations:
                    ann_id = ann.get('id')
                    is_editing = st.session_state.editing_annotation == ann_id
                    
                    if not is_editing:
                        # 正常顯示模式
                        col_ann, col_edit, col_del = st.columns([3, 1, 1])
                        with col_ann:
                            st.markdown(f"- **{ann.get('variable_name', '無名變數')}** (`{ann.get('variable_type', '未知類型')}`)")
                            if ann.get('sample_value'):
                                st.caption(f"範例：{ann.get('sample_value')}")
                        with col_edit:
                            if st.button("✏️", key=f"edit_ann_{ann_id}", help="編輯此標記"):
                                st.session_state.editing_annotation = ann_id
                                st.rerun()
                        with col_del:
                            if st.button("🗑️", key=f"delete_ann_{ann_id}", help="刪除此標記"):
                                if system.delete_annotation(ann_id):
                                    st.success(f"已刪除標記 '{ann.get('variable_name')}'")
                                    st.rerun()
                                else:
                                    st.error("刪除失敗")
                    else:
                        # 編輯模式
                        st.markdown(f"🔧 **編輯標記：{ann.get('variable_name')}**")
                        with st.form(key=f"edit_form_{ann_id}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                edit_name = st.text_input(
                                    "變數名稱", 
                                    value=ann.get('variable_name', ''),
                                    key=f"edit_name_{ann_id}"
                                )
                                edit_type = st.selectbox(
                                    "變數類型", 
                                    ["文字", "數字", "日期", "地址", "其他"],
                                    index=["文字", "數字", "日期", "地址", "其他"].index(ann.get('variable_type', '文字')) if ann.get('variable_type') in ["文字", "數字", "日期", "地址", "其他"] else 0,
                                    key=f"edit_type_{ann_id}"
                                )
                            with col2:
                                edit_sample = st.text_input(
                                    "範例值", 
                                    value=ann.get('sample_value', ''),
                                    key=f"edit_sample_{ann_id}"
                                )
                                st.markdown("**目前座標：**")
                                st.caption(f"({ann.get('x_start', 0):.0f}, {ann.get('y_start', 0):.0f}) - ({ann.get('x_end', 0):.0f}, {ann.get('y_end', 0):.0f})")
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 儲存變更", use_container_width=True):
                                    if edit_name:
                                        coords = (ann.get('x_start', 0), ann.get('y_start', 0), 
                                                ann.get('x_end', 0), ann.get('y_end', 0))
                                        if system.update_annotation(ann_id, edit_name, edit_type, coords, edit_sample):
                                            st.success(f"✅ 標記 '{edit_name}' 已更新")
                                            st.session_state.editing_annotation = None
                                            st.rerun()
                                        else:
                                            st.error("更新失敗")
                                    else:
                                        st.error("請填寫變數名稱")
                            
                            with col_cancel:
                                if st.form_submit_button("❌ 取消編輯", use_container_width=True):
                                    st.session_state.editing_annotation = None
                                    st.rerun()
                        
                        st.markdown("---")
            else:
                if page_type == "變數頁面":
                    st.caption("此變數頁面尚無標記。")
                else:
                    note_text = f"（{page_note}）" if page_note else ""
                    st.caption(f"此參考資料頁面{note_text}不需要標記變數。")

def variable_database_tab(system: PDFAnnotationSystem):
    st.markdown("### 📊 變數資料庫")
    variables = system.get_variable_database()
    if variables:
        df_data = [{
            '變數名稱': v.get('variable_name', '無名變數'), '類型': v.get('variable_type', '未知'),
            '使用次數': v.get('usage_count', 0), '範例數量': len(v.get('sample_values', [])),
            '最新範例': v.get('sample_values', [])[-1] if v.get('sample_values') else '',
            '更新時間': v.get('updated_at', '未知')
        } for v in variables]
        st.dataframe(pd.DataFrame(df_data), use_container_width=True)
    else:
        st.info("📝 變數資料庫為空。")

def template_management_tab(system: PDFAnnotationSystem):
    st.markdown("### 🔍 範本管理")
    templates = system.get_templates_list()
    if templates:
        for template in templates:
            template_id = template.get('id')
            template_name = template.get('name', f"未命名範本 (ID: {template_id})")
            total_pages = template.get('total_pages', 0)
            if not template_id:
                st.warning(f"發現一筆無效的範本資料：{template}")
                continue
            
            # 取得頁面類型統計
            page_types = system.get_template_page_types(template_id)
            page_info = system.get_template_page_info(template_id)
            variable_pages = sum(1 for page_type in page_types.values() if page_type == '變數頁面')
            reference_pages = sum(1 for page_type in page_types.values() if page_type == '參考資料')
            undefined_pages = total_pages - len(page_types)
            
            with st.expander(f"📄 {template_name} ({total_pages} 頁)"):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**描述：** {template.get('description', '無')}")
                    annotations = system.get_template_annotations(template_id)
                    st.write(f"**變數標記數：** {len(annotations)}")
                    
                with col2:
                    st.write(f"**建立時間：** {template.get('created_at', '未知')}")
                    st.write(f"**更新時間：** {template.get('updated_at', '未知')}")
                    
                with col3:
                    if st.button("🗑️ 刪除", key=f"delete_{template_id}"):
                        if system.delete_template(template_id, total_pages):
                            st.success(f"✅ 範本 '{template_name}' 已成功刪除！")
                            st.rerun()
                        else:
                            st.error(f"❌ 刪除範本 '{template_name}' 失敗。")
                
                # 頁面類型統計
                st.markdown("**📋 頁面類型分佈：**")
                col_var, col_ref, col_undef = st.columns(3)
                with col_var:
                    st.metric("📝 變數頁面", variable_pages)
                with col_ref:
                    st.metric("📄 參考資料", reference_pages)
                with col_undef:
                    st.metric("⚪ 未設定", undefined_pages)
                
                # 詳細頁面資訊
                if st.checkbox(f"顯示詳細頁面資訊", key=f"detail_{template_id}"):
                    st.markdown("**📄 各頁面詳情：**")
                    
                    for page_num in range(1, total_pages + 1):
                        page_type = page_types.get(page_num, '變數頁面')  # 預設為變數頁面
                        page_note = page_info.get(page_num, {}).get('note', '')
                        page_annotations = system.get_template_annotations(template_id, page_num)
                        
                        if page_type == '變數頁面':
                            type_icon = "📝"
                            type_name = "變數頁面"
                            note_display = ""
                        else:
                            type_icon = "📄"
                            type_name = "參考資料"
                            note_display = f" - {page_note}" if page_note else ""
                        
                        st.write(f"　第 {page_num} 頁：{type_icon} {type_name}{note_display} ({len(page_annotations)} 個標記)")
    else:
        st.info("📝 尚無範本，請先上傳 PDF 檔案。")