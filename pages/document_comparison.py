# 檔名: pages/document_comparison.py
# PDF文件比對檢查頁面

import streamlit as st
import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from PIL import Image

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pdf_annotation_system import PDFAnnotationSystem

class DocumentComparison:
    def __init__(self):
        if 'annotation_system' not in st.session_state:
            st.session_state.annotation_system = PDFAnnotationSystem()
        self.system = st.session_state.annotation_system
        
    def show_document_comparison(self):
        """顯示文件比對檢查頁面"""
        st.markdown("## 🔍 文件比對檢查")
        st.markdown("上傳待檢查的PDF文件，與範本進行智慧比對並產生缺失清單")
        
        # 檢查是否有可用的範本
        templates = self.system.get_templates_list()
        if not templates:
            st.warning("⚠️ 尚未建立任何PDF範本，請先到「PDF變數標記」頁面上傳並標記範本。")
            return
        
        # 創建頁籤
        tab1, tab2, tab3, tab4 = st.tabs(["📤 上傳檔案", "🔍 執行比對", "📋 比對結果", "📁 下載報告"])
        
        with tab1:
            self._show_upload_tab(templates)
        with tab2:
            self._show_comparison_tab()
        with tab3:
            self._show_results_tab()
        with tab4:
            self._show_download_tab()
    
    def _show_upload_tab(self, templates: List[Dict]):
        """顯示檔案上傳頁籤"""
        st.markdown("### 📤 上傳待檢查的PDF文件")
        
        # 範本選擇區域
        st.markdown("#### 🎯 選擇比對範本群組")
        st.info("💡 您可以選擇多個範本作為比對基準，系統會與每個範本進行比對以提高準確性。")
        
        # 顯示可用範本
        template_options = {}
        for template in templates:
            template_id = template['id']
            template_name = template['name']
            description = template.get('description', '無描述')
            annotations_count = len(self.system.get_template_annotations(template_id))
            
            template_options[f"{template_name} ({annotations_count} 個變數)"] = {
                'id': template_id,
                'name': template_name,
                'description': description,
                'annotations_count': annotations_count
            }
        
        # 多選範本
        selected_template_names = st.multiselect(
            "選擇要使用的範本（建議選擇3-5個相關範本）",
            list(template_options.keys()),
            help="選擇多個範本可以提高比對的準確性"
        )
        
        if not selected_template_names:
            st.warning("⚠️ 請至少選擇一個範本進行比對。")
            return
        
        # 顯示選中的範本資訊
        st.markdown("#### 📋 已選擇的範本")
        for template_name in selected_template_names:
            template_info = template_options[template_name]
            template_id = template_info['id']
            
            # 取得頁面類型統計
            page_types = self.system.get_template_page_types(template_id)
            page_info = self.system.get_template_page_info(template_id)
            variable_pages = sum(1 for page_type in page_types.values() if page_type == '變數頁面')
            reference_pages = sum(1 for page_type in page_types.values() if page_type == '參考資料')
            
            with st.expander(f"📄 {template_info['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**描述：** {template_info['description']}")
                    st.write(f"**變數數量：** {template_info['annotations_count']}")
                    st.write(f"**📝 變數頁面：** {variable_pages} 頁")
                    st.write(f"**📄 參考資料：** {reference_pages} 頁")
                with col2:
                    # 顯示範本預覽（第一頁）
                    try:
                        page_image = self.system.load_template_page(template_id, 1)
                        if page_image:
                            # 縮小圖片顯示
                            thumbnail = page_image.copy()
                            thumbnail.thumbnail((200, 300))
                            page_type, page_note = self.system.get_page_info(template_id, 1)
                            if page_type == "變數頁面":
                                type_label = "📝 變數頁面"
                            else:
                                note_display = f" - {page_note}" if page_note else ""
                                type_label = f"📄 參考資料{note_display}"
                            st.image(thumbnail, caption=f"第1頁預覽 ({type_label})")
                    except:
                        st.write("無法載入預覽")
        
        # 檔案上傳區域
        st.markdown("#### 📁 上傳待檢查的PDF文件")
        
        uploaded_file = st.file_uploader(
            "選擇PDF檔案",
            type=['pdf'],
            help="支援多頁PDF文件，系統會自動與選中的範本進行比對"
        )
        
        if uploaded_file:
            # 顯示上傳檔案資訊
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
            st.success(f"✅ 已上傳檔案：**{uploaded_file.name}** ({file_size:.2f} MB)")
            
            # 處理上傳的PDF
            with st.spinner("正在處理上傳的PDF..."):
                try:
                    # 轉換PDF為圖片
                    uploaded_images = self.system.convert_pdf_to_images(uploaded_file)
                    
                    if uploaded_images:
                        st.success(f"✅ PDF處理成功，共 {len(uploaded_images)} 頁")
                        
                        # 儲存到session state
                        st.session_state['uploaded_file_name'] = uploaded_file.name
                        st.session_state['uploaded_images'] = uploaded_images
                        st.session_state['selected_templates'] = [
                            template_options[name] for name in selected_template_names
                        ]
                        
                        # 顯示上傳檔案預覽
                        st.markdown("#### 👀 上傳檔案預覽")
                        preview_pages = min(3, len(uploaded_images))  # 最多顯示3頁
                        
                        cols = st.columns(preview_pages)
                        for i in range(preview_pages):
                            with cols[i]:
                                thumbnail = uploaded_images[i].copy()
                                thumbnail.thumbnail((200, 300))
                                st.image(thumbnail, caption=f"第 {i+1} 頁")
                        
                        if len(uploaded_images) > 3:
                            st.info(f"... 還有 {len(uploaded_images) - 3} 頁未顯示")
                        
                        st.success("🚀 準備就緒！請切換到「執行比對」頁籤開始比對。")
                        
                    else:
                        st.error("❌ PDF處理失敗，請檢查檔案格式是否正確。")
                        
                except Exception as e:
                    st.error(f"處理PDF時發生錯誤：{str(e)}")
    
    def _show_comparison_tab(self):
        """顯示比對執行頁籤"""
        st.markdown("### 🔍 執行文件比對")
        
        # 檢查是否有上傳的檔案和選中的範本
        if 'uploaded_images' not in st.session_state or 'selected_templates' not in st.session_state:
            st.info("💡 請先在「上傳檔案」頁籤上傳PDF並選擇範本。")
            return
        
        uploaded_images = st.session_state['uploaded_images']
        selected_templates = st.session_state['selected_templates']
        file_name = st.session_state.get('uploaded_file_name', '未知檔案')
        
        # 顯示比對摘要
        st.markdown("#### 📋 比對摘要")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("上傳檔案", file_name)
            st.metric("檔案頁數", len(uploaded_images))
        with col2:
            st.metric("範本數量", len(selected_templates))
            total_variables = sum(template['annotations_count'] for template in selected_templates)
            st.metric("總變數數量", total_variables)
        
        # 比對設定
        st.markdown("#### ⚙️ 比對設定")
        
        col1, col2 = st.columns(2)
        with col1:
            strict_mode = st.checkbox(
                "嚴格模式",
                value=True,
                help="標記頁面必須完全匹配，參考頁面允許相似度比對"
            )
            
            similarity_threshold = st.slider(
                "相似度閾值 (%)",
                min_value=50,
                max_value=95,
                value=80,
                help="參考頁面的最低相似度要求"
            )
        
        with col2:
            generate_preview = st.checkbox(
                "生成預覽圖",
                value=True,
                help="在比對結果中包含預覽圖片"
            )
            
            detailed_report = st.checkbox(
                "詳細報告",
                value=True,
                help="包含每個變數的詳細比對資訊"
            )
        
        # 執行比對按鈕
        st.markdown("#### 🚀 開始比對")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 執行智慧比對", use_container_width=True, type="primary"):
                with st.spinner("正在執行智慧比對，請稍候..."):
                    comparison_results = self._perform_comparison(
                        uploaded_images,
                        selected_templates,
                        strict_mode,
                        similarity_threshold,
                        generate_preview,
                        detailed_report
                    )
                    
                    if comparison_results:
                        st.session_state['comparison_results'] = comparison_results
                        st.success("✅ 比對完成！請切換到「比對結果」頁籤查看結果。")
                        st.balloons()
                    else:
                        st.error("❌ 比對過程發生錯誤，請稍後再試。")
    
    def _show_results_tab(self):
        """顯示比對結果頁籤"""
        st.markdown("### 📋 比對結果")
        
        if 'comparison_results' not in st.session_state:
            st.info("💡 請先在「執行比對」頁籤完成文件比對。")
            return
        
        results = st.session_state['comparison_results']
        
        # 顯示總體結果
        st.markdown("#### 📊 總體結果")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("總變數數量", results.get('total_variables', 0))
        with col2:
            passed = results.get('passed_variables', 0)
            st.metric("通過變數", passed, delta=None)
        with col3:
            failed = results.get('failed_variables', 0)
            st.metric("失敗變數", failed, delta=None)
        with col4:
            success_rate = (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0
            st.metric("成功率", f"{success_rate:.1f}%")
        
        # 顯示詳細結果
        st.markdown("#### 📝 詳細結果")
        
        # 按範本顯示結果
        for template_result in results.get('template_results', []):
            template_name = template_result['template_name']
            template_passed = template_result.get('passed', 0)
            template_failed = template_result.get('failed', 0)
            template_total = template_passed + template_failed
            
            with st.expander(f"📄 {template_name} ({template_passed}/{template_total} 通過)"):
                
                # 顯示變數比對結果
                variable_results = template_result.get('variable_results', [])
                page_results = template_result.get('page_results', [])
                
                if variable_results or page_results:
                    # 創建變數比對結果表格
                    if variable_results:
                        st.markdown("**📝 變數頁面比對結果：**")
                        df_data = []
                        for var_result in variable_results:
                            df_data.append({
                                '變數名稱': var_result.get('variable_name', ''),
                                '變數類型': var_result.get('variable_type', ''),
                                '頁面': f"第{var_result.get('page_number', '')}頁",
                                '頁面類型': var_result.get('page_type', ''),
                                '狀態': '✅ 通過' if var_result.get('passed', False) else '❌ 失敗',
                                '精確度': f"{var_result.get('similarity', 0):.1f}%",
                                '備註': var_result.get('note', '')
                            })
                        
                        df = pd.DataFrame(df_data)
                        st.dataframe(df, use_container_width=True)
                    
                    # 創建頁面相似度比對結果表格
                    if page_results:
                        st.markdown("**📄 參考資料頁面比對結果：**")
                        df_page_data = []
                        for page_result in page_results:
                            df_page_data.append({
                                '頁面': f"第{page_result.get('page_number', '')}頁",
                                '頁面類型': page_result.get('page_type', ''),
                                '狀態': '✅ 通過' if page_result.get('passed', False) else '❌ 失敗',
                                '相似度': f"{page_result.get('similarity', 0):.1f}%",
                                '備註': page_result.get('note', '')
                            })
                        
                        df_page = pd.DataFrame(df_page_data)
                        st.dataframe(df_page, use_container_width=True)
                else:
                    st.info("此範本沒有比對結果。")
        
        # 顯示失敗項目摘要
        failed_items = results.get('failed_items', [])
        if failed_items:
            st.markdown("#### ⚠️ 需要注意的項目")
            
            # 按頁面類型分組顯示失敗項目
            variable_failures = [item for item in failed_items if item.get('page_type') == '變數頁面']
            reference_failures = [item for item in failed_items if item.get('page_type') == '參考資料']
            
            if variable_failures:
                st.markdown("**📝 變數頁面問題：**")
                for item in variable_failures:
                    st.error(f"❌ **{item.get('variable_name', '未知變數')}** - {item.get('reason', '未知原因')}")
            
            if reference_failures:
                st.markdown("**📄 參考資料頁面問題：**")
                for item in reference_failures:
                    st.warning(f"⚠️ **{item.get('variable_name', '未知頁面')}** - {item.get('reason', '未知原因')}")
            
            # 其他未分類的失敗項目
            other_failures = [item for item in failed_items 
                            if item.get('page_type') not in ['變數頁面', '參考資料']]
            if other_failures:
                st.markdown("**❓ 其他問題：**")
                for item in other_failures:
                    st.error(f"❌ **{item.get('variable_name', '未知項目')}** - {item.get('reason', '未知原因')}")
    
    def _show_download_tab(self):
        """顯示報告下載頁籤"""
        st.markdown("### 📁 下載比對報告")
        
        if 'comparison_results' not in st.session_state:
            st.info("💡 請先完成文件比對才能下載報告。")
            return
        
        results = st.session_state['comparison_results']
        
        # 報告格式選擇
        st.markdown("#### 📋 選擇報告格式")
        
        col1, col2 = st.columns(2)
        with col1:
            report_format = st.selectbox(
                "報告格式",
                ["PDF報告", "Word文檔", "Excel表格"],
                help="選擇您需要的報告格式"
            )
        with col2:
            include_images = st.checkbox(
                "包含圖片",
                value=True,
                help="在報告中包含比對的圖片預覽"
            )
        
        # 報告內容選項
        st.markdown("#### 📝 報告內容")
        
        col1, col2 = st.columns(2)
        with col1:
            include_summary = st.checkbox("包含總結", value=True)
            include_details = st.checkbox("包含詳細資訊", value=True)
        with col2:
            include_recommendations = st.checkbox("包含改善建議", value=True)
            include_statistics = st.checkbox("包含統計圖表", value=False)
        
        # 生成報告按鈕
        st.markdown("#### 🚀 生成報告")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📄 生成並下載報告", use_container_width=True, type="primary"):
                with st.spinner("正在生成報告..."):
                    success = self._generate_report(
                        results,
                        report_format,
                        include_images,
                        include_summary,
                        include_details,
                        include_recommendations,
                        include_statistics
                    )
                    
                    if success:
                        st.success("✅ 報告生成成功！")
                    else:
                        st.error("❌ 報告生成失敗，請稍後再試。")
    
    def _perform_comparison(self, uploaded_images: List[Image.Image], selected_templates: List[Dict], 
                          strict_mode: bool, similarity_threshold: float, 
                          generate_preview: bool, detailed_report: bool) -> Dict:
        """執行文件比對"""
        try:
            # TODO: 實現實際的比對邏輯
            # 1. 對每個範本進行比對
            # 2. 檢查標記變數的精確度（變數頁面）
            # 3. 計算參考頁面相似度（參考資料頁面）
            # 4. 生成比對結果
            
            # 模擬比對結果
            results = {
                'total_variables': 0,
                'passed_variables': 0,
                'failed_variables': 0,
                'template_results': [],
                'failed_items': [],
                'page_comparison_results': [],  # 新增頁面比對結果
                'comparison_time': datetime.now().isoformat()
            }
            
            for template in selected_templates:
                template_id = template['id']
                template_name = template['name']
                annotations = self.system.get_template_annotations(template_id)
                page_types = self.system.get_template_page_types(template_id)
                
                # 模擬變數比對結果（只針對變數頁面）
                variable_results = []
                passed_count = 0
                failed_count = 0
                
                for ann in annotations:
                    page_num = ann['page_number']
                    page_type = page_types.get(page_num, '變數頁面')
                    
                    # 只對變數頁面進行精確比對
                    if page_type == '變數頁面':
                        # 模擬比對結果
                        import random
                        similarity = random.uniform(60, 95)
                        
                        if strict_mode:
                            # 嚴格模式：變數頁面要求更高精確度
                            passed = similarity >= min(similarity_threshold + 10, 95)
                        else:
                            passed = similarity >= similarity_threshold
                        
                        if passed:
                            passed_count += 1
                        else:
                            failed_count += 1
                            results['failed_items'].append({
                                'variable_name': ann['variable_name'],
                                'page_type': '變數頁面',
                                'reason': f"變數 '{ann['variable_name']}' 精確度 {similarity:.1f}% 低於要求"
                            })
                        
                        variable_results.append({
                            'variable_name': ann['variable_name'],
                            'variable_type': ann['variable_type'],
                            'page_number': page_num,
                            'page_type': '變數頁面',
                            'passed': passed,
                            'similarity': similarity,
                            'note': '精確比對通過' if passed else '精確比對失敗'
                        })
                
                # 模擬頁面相似度比對結果（參考資料頁面）
                page_results = []
                for page_num in range(1, template.get('total_pages', 1) + 1):
                    page_type = page_types.get(page_num, '變數頁面')
                    
                    if page_type == '參考資料':
                        # 參考資料頁面使用相似度比對
                        import random
                        page_similarity = random.uniform(50, 90)
                        page_passed = page_similarity >= similarity_threshold
                        
                        page_results.append({
                            'page_number': page_num,
                            'page_type': '參考資料',
                            'similarity': page_similarity,
                            'passed': page_passed,
                            'note': '相似度比對通過' if page_passed else '相似度比對失敗'
                        })
                        
                        if not page_passed:
                            results['failed_items'].append({
                                'variable_name': f'第{page_num}頁（參考資料）',
                                'page_type': '參考資料',
                                'reason': f"頁面相似度 {page_similarity:.1f}% 低於閾值 {similarity_threshold}%"
                            })
                
                results['template_results'].append({
                    'template_name': template_name,
                    'passed': passed_count,
                    'failed': failed_count,
                    'variable_results': variable_results,
                    'page_results': page_results  # 新增頁面比對結果
                })
                
                results['total_variables'] += len([ann for ann in annotations 
                                                 if page_types.get(ann['page_number'], '變數頁面') == '變數頁面'])
                results['passed_variables'] += passed_count
                results['failed_variables'] += failed_count
            
            return results
            
        except Exception as e:
            st.error(f"比對過程發生錯誤：{str(e)}")
            return None
    
    def _generate_report(self, results: Dict, report_format: str, include_images: bool,
                        include_summary: bool, include_details: bool, 
                        include_recommendations: bool, include_statistics: bool) -> bool:
        """生成比對報告"""
        try:
            # TODO: 實現實際的報告生成邏輯
            # 1. 根據選擇的格式生成報告
            # 2. 包含選中的內容
            # 3. 提供下載連結
            
            st.info("🚧 報告生成功能正在開發中...")
            st.write("**報告內容預覽：**")
            st.json(results)
            
            return True
            
        except Exception as e:
            st.error(f"生成報告時發生錯誤：{str(e)}")
            return False

def document_comparison_page():
    """文件比對檢查頁面入口"""
    comparison = DocumentComparison()
    comparison.show_document_comparison()

if __name__ == "__main__":
    document_comparison_page()