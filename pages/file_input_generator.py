# 檔名: pages/file_input_generator.py
# PDF範本文字輸入與檔案生成頁面

import streamlit as st
import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, List
from PIL import Image

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pdf_annotation_system import PDFAnnotationSystem

class FileInputGenerator:
    def __init__(self):
        if 'annotation_system' not in st.session_state:
            st.session_state.annotation_system = PDFAnnotationSystem()
        self.system = st.session_state.annotation_system
        
    def show_file_input_generator(self):
        """顯示檔案輸入與生成頁面"""
        st.markdown("## 📝 檔案輸入與生成")
        st.markdown("根據PDF範本輸入變數值，生成與範本一致的文件")
        
        # 檢查是否有可用的範本
        templates = self.system.get_templates_list()
        if not templates:
            st.warning("⚠️ 尚未建立任何PDF範本，請先到「PDF變數標記」頁面上傳並標記範本。")
            return
        
        # 創建頁籤
        tab1, tab2, tab3 = st.tabs(["📝 輸入資料", "🎯 生成文件", "📄 歷史記錄"])
        
        with tab1:
            self._show_input_tab(templates)
        with tab2:
            self._show_generation_tab()
        with tab3:
            self._show_history_tab()
    
    def _show_input_tab(self, templates: List[Dict]):
        """顯示資料輸入頁籤"""
        st.markdown("### 📝 選擇範本並輸入資料")
        
        # 範本選擇
        template_names = [t['name'] for t in templates]
        selected_template_name = st.selectbox("選擇要使用的範本", template_names)
        
        if not selected_template_name:
            return
            
        # 獲取選中的範本
        selected_template = next(t for t in templates if t['name'] == selected_template_name)
        template_id = selected_template['id']
        
        # 顯示範本資訊
        with st.expander(f"📄 範本資訊 - {selected_template_name}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**描述：** {selected_template.get('description', '無')}")
                st.write(f"**總頁數：** {selected_template.get('total_pages', 0)}")
            with col2:
                st.write(f"**建立時間：** {selected_template.get('created_at', '未知')}")
                st.write(f"**更新時間：** {selected_template.get('updated_at', '未知')}")
        
        # 獲取範本的所有變數
        annotations = self.system.get_template_annotations(template_id)
        if not annotations:
            st.warning("⚠️ 此範本尚未標記任何變數，請先到「PDF變數標記」頁面進行標記。")
            return
        
        # 按頁面分組變數
        variables_by_page = {}
        for ann in annotations:
            page_num = ann['page_number']
            if page_num not in variables_by_page:
                variables_by_page[page_num] = []
            variables_by_page[page_num].append(ann)
        
        # 初始化session state中的輸入值
        if f'input_values_{template_id}' not in st.session_state:
            st.session_state[f'input_values_{template_id}'] = {}
        
        # 顯示變數輸入表單
        st.markdown("### ✏️ 輸入變數值")
        
        with st.form(f"input_form_{template_id}"):
            # 按頁面顯示變數
            for page_num in sorted(variables_by_page.keys()):
                st.markdown(f"#### 📄 第 {page_num} 頁")
                
                variables = variables_by_page[page_num]
                for variable in variables:
                    var_name = variable['variable_name']
                    var_type = variable['variable_type']
                    sample_value = variable.get('sample_value', '')
                    
                    # 根據變數類型選擇適當的輸入控件
                    if var_type == "日期":
                        value = st.date_input(
                            f"{var_name} ({var_type})",
                            help=f"範例值：{sample_value}" if sample_value else None,
                            key=f"date_{template_id}_{page_num}_{var_name}"  # 添加唯一key
                        )
                        st.session_state[f'input_values_{template_id}'][var_name] = value.strftime("%Y-%m-%d") if value else ""
                    elif var_type == "數字":
                        value = st.number_input(
                            f"{var_name} ({var_type})",
                            help=f"範例值：{sample_value}" if sample_value else None,
                            key=f"number_{template_id}_{page_num}_{var_name}"  # 添加唯一key
                        )
                        st.session_state[f'input_values_{template_id}'][var_name] = str(value)
                    else:  # 文字、地址、其他
                        value = st.text_input(
                            f"{var_name} ({var_type})",
                            placeholder=f"範例：{sample_value}" if sample_value else f"請輸入{var_name}",
                            help=f"範例值：{sample_value}" if sample_value else None,
                            key=f"input_{template_id}_{page_num}_{var_name}"  # 添加唯一key
                        )
                        st.session_state[f'input_values_{template_id}'][var_name] = value
                
                if page_num < max(variables_by_page.keys()):
                    st.markdown("---")
            
            # 提交按鈕
            submitted = st.form_submit_button("💾 儲存輸入資料", use_container_width=True)
            
            if submitted:
                # 驗證必填欄位
                missing_fields = []
                for var_name, value in st.session_state[f'input_values_{template_id}'].items():
                    if not value or str(value).strip() == "":
                        missing_fields.append(var_name)
                
                if missing_fields:
                    st.error(f"❌ 請填寫以下必填欄位：{', '.join(missing_fields)}")
                else:
                    # 儲存到session state
                    st.session_state['current_template_id'] = template_id
                    st.session_state['current_template_name'] = selected_template_name
                    st.success("✅ 資料已儲存！請切換到「生成文件」頁籤產出檔案。")
    
    def _show_generation_tab(self):
        """顯示文件生成頁籤"""
        st.markdown("### 🎯 生成文件")
        
        # 檢查是否有輸入資料
        if 'current_template_id' not in st.session_state:
            st.info("💡 請先在「輸入資料」頁籤選擇範本並輸入變數值。")
            return
        
        template_id = st.session_state['current_template_id']
        template_name = st.session_state['current_template_name']
        input_values = st.session_state.get(f'input_values_{template_id}', {})
        
        if not input_values:
            st.warning("⚠️ 沒有找到輸入資料，請重新輸入。")
            return
        
        # 顯示當前資料摘要
        st.markdown(f"#### 📋 當前範本：{template_name}")
        
        with st.expander("📝 查看輸入資料"):
            for var_name, value in input_values.items():
                st.write(f"**{var_name}：** {value}")
        
        # 生成選項
        st.markdown("#### ⚙️ 生成選項")
        
        col1, col2 = st.columns(2)
        with col1:
            output_format = st.selectbox(
                "輸出格式",
                ["PDF（推薦）", "PNG圖片"],
                help="PDF格式保持最佳品質，PNG適合預覽"
            )
        with col2:
            output_name = st.text_input(
                "檔案名稱",
                value=f"{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                help="不需要加副檔名"
            )
        
        # 生成按鈕
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 生成文件", use_container_width=True, type="primary"):
                with st.spinner("正在生成文件..."):
                    success = self._generate_document(
                        template_id, 
                        input_values, 
                        output_name, 
                        output_format
                    )
                    
                    if success:
                        st.success("✅ 文件生成成功！")
                        st.balloons()
                    else:
                        st.error("❌ 文件生成失敗，請稍後再試。")
    
    def _show_history_tab(self):
        """顯示歷史記錄頁籤"""
        st.markdown("### 📄 生成歷史記錄")
        st.info("🚧 此功能正在開發中...")
        
        # TODO: 實現歷史記錄功能
        # - 顯示過去生成的文件列表
        # - 提供重新下載功能
        # - 顯示生成時間和參數
    
    def _generate_document(self, template_id: int, input_values: Dict, output_name: str, output_format: str) -> bool:
        """生成文件"""
        try:
            # 獲取範本資訊
            template_info = self.system.get_template_info(template_id)
            if not template_info:
                st.error("❌ 無法獲取範本資訊")
                return False
            
            # 獲取範本的所有註解
            annotations = self.system.get_template_annotations(template_id)
            if not annotations:
                st.error("❌ 範本沒有標記任何變數")
                return False
            
            # 創建輸出目錄
            output_dir = "generated_files"
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件
            if output_format == "PDF（推薦）":
                success = self._generate_pdf(template_info, annotations, input_values, output_name, output_dir)
            else:  # PNG圖片
                success = self._generate_image(template_info, annotations, input_values, output_name, output_dir)
            
            if success:
                # 提供下載連結
                if output_format == "PDF（推薦）":
                    file_path = os.path.join(output_dir, f"{output_name}.pdf")
                    mime_type = "application/pdf"
                else:  # PNG圖片
                    file_path = os.path.join(output_dir, f"{output_name}.png")
                    mime_type = "image/png"
                
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    
                    st.download_button(
                        label="📥 下載生成的文件",
                        data=file_data,
                        file_name=os.path.basename(file_path),
                        mime=mime_type
                    )
                else:
                    st.error(f"❌ 生成的文件不存在：{file_path}")
            
            return success
            
        except Exception as e:
            st.error(f"生成文件時發生錯誤：{str(e)}")
            return False
    
    def _generate_pdf(self, template_info: Dict, annotations: List[Dict], input_values: Dict, output_name: str, output_dir: str) -> bool:
        """生成PDF文件 - 在原始範本上填入變數值"""
        try:
            import fitz  # PyMuPDF
            
            # 載入原始PDF範本
            template_id = template_info['id']
            original_pdf_path = os.path.join(self.system.templates_dir, f"{template_id}_original.pdf")
            
            if not os.path.exists(original_pdf_path):
                st.error("❌ 找不到原始PDF範本文件")
                return False
            
            # 打開原始PDF
            doc = fitz.open(original_pdf_path)
            
            # 按頁面處理變數替換
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # 獲取當前頁面的變數標記
                page_annotations = [ann for ann in annotations if ann['page_number'] == page_num + 1]
                
                for annotation in page_annotations:
                    var_name = annotation['variable_name']
                    if var_name in input_values:
                        # 獲取變數值
                        var_value = input_values[var_name]
                        
                        # 獲取標記的座標
                        x_start = annotation['x_start']
                        y_start = annotation['y_start']
                        x_end = annotation['x_end']
                        y_end = annotation['y_end']
                        
                        # 計算文字位置和大小
                        rect = fitz.Rect(x_start, y_start, x_end, y_end)
                        
                        # 在標記位置填入變數值
                        page.insert_text(
                            rect.tl,  # 左上角位置
                            str(var_value),
                            fontsize=12,  # 字體大小
                            color=(0, 0, 0),  # 黑色
                            fontname="helv"  # 字體
                        )
            
            # 保存生成的PDF
            output_path = os.path.join(output_dir, f"{output_name}.pdf")
            doc.save(output_path)
            doc.close()
            
            st.success(f"✅ PDF文件已生成：{output_path}")
            return True
            
        except Exception as e:
            st.error(f"生成PDF時發生錯誤：{str(e)}")
            return False
    
    def _generate_image(self, template_info: Dict, annotations: List[Dict], input_values: Dict, output_name: str, output_dir: str) -> bool:
        """生成圖片文件 - 在原始範本圖片上填入變數值"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 載入原始範本圖片
            template_id = template_info['id']
            total_pages = template_info.get('total_pages', 0)
            
            # 創建圖片列表
            generated_images = []
            
            for page_num in range(1, total_pages + 1):
                # 載入原始頁面圖片
                image_path = os.path.join(self.system.templates_dir, f"{template_id}_page_{page_num}.png")
                
                if not os.path.exists(image_path):
                    st.error(f"❌ 找不到第{page_num}頁的圖片文件")
                    return False
                
                # 打開原始圖片
                img = Image.open(image_path)
                draw = ImageDraw.Draw(img)
                
                # 嘗試載入字體（如果失敗則使用預設字體）
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except:
                    font = ImageFont.load_default()
                
                # 獲取當前頁面的變數標記
                page_annotations = [ann for ann in annotations if ann['page_number'] == page_num]
                
                for annotation in page_annotations:
                    var_name = annotation['variable_name']
                    if var_name in input_values:
                        # 獲取變數值
                        var_value = input_values[var_name]
                        
                        # 獲取標記的座標
                        x_start = annotation['x_start']
                        y_start = annotation['y_start']
                        x_end = annotation['x_end']
                        y_end = annotation['y_end']
                        
                        # 在標記位置填入變數值
                        draw.text(
                            (x_start, y_start),
                            str(var_value),
                            fill=(0, 0, 0),  # 黑色
                            font=font
                        )
                
                generated_images.append(img)
            
            # 保存生成的圖片
            if len(generated_images) == 1:
                # 單頁圖片
                output_path = os.path.join(output_dir, f"{output_name}.png")
                generated_images[0].save(output_path)
            else:
                # 多頁圖片，保存為PDF
                output_path = os.path.join(output_dir, f"{output_name}.pdf")
                generated_images[0].save(
                    output_path,
                    "PDF",
                    save_all=True,
                    append_images=generated_images[1:]
                )
            
            st.success(f"✅ 圖片文件已生成：{output_path}")
            return True
            
        except Exception as e:
            st.error(f"生成圖片時發生錯誤：{str(e)}")
            return False

def file_input_generation_page():
    """檔案輸入與生成頁面入口"""
    generator = FileInputGenerator()
    generator.show_file_input_generator()

if __name__ == "__main__":
    file_input_generation_page()