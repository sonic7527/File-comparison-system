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
                            help=f"範例值：{sample_value}" if sample_value else None
                        )
                        st.session_state[f'input_values_{template_id}'][var_name] = value.strftime("%Y-%m-%d") if value else ""
                    elif var_type == "數字":
                        value = st.number_input(
                            f"{var_name} ({var_type})",
                            help=f"範例值：{sample_value}" if sample_value else None
                        )
                        st.session_state[f'input_values_{template_id}'][var_name] = str(value)
                    else:  # 文字、地址、其他
                        value = st.text_input(
                            f"{var_name} ({var_type})",
                            placeholder=f"範例：{sample_value}" if sample_value else f"請輸入{var_name}",
                            help=f"範例值：{sample_value}" if sample_value else None
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
            # TODO: 實現實際的文件生成邏輯
            # 1. 載入PDF範本
            # 2. 在指定位置填入變數值
            # 3. 生成新的PDF或圖片
            # 4. 提供下載
            
            st.info("🚧 文件生成功能正在開發中...")
            st.write("**將要生成的內容：**")
            st.json(input_values)
            
            return True
            
        except Exception as e:
            st.error(f"生成文件時發生錯誤：{str(e)}")
            return False

def file_input_generation_page():
    """檔案輸入與生成頁面入口"""
    generator = FileInputGenerator()
    generator.show_file_input_generator()

if __name__ == "__main__":
    file_input_generation_page()