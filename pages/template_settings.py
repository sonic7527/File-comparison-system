# 檔名: pages/template_settings.py
# 範本管理設定頁面

import streamlit as st
import os
import sys
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pdf_annotation_system import PDFAnnotationSystem

class TemplateSettings:
    def __init__(self):
        if 'annotation_system' not in st.session_state:
            st.session_state.annotation_system = PDFAnnotationSystem()
        self.system = st.session_state.annotation_system
        
    def show_template_settings(self):
        """顯示範本管理設定頁面"""
        st.markdown("## ⚙️ 範本管理設定")
        st.markdown("管理範本群組、分類和使用統計")
        
        # 創建頁籤
        tab1, tab2, tab3, tab4 = st.tabs(["📂 範本群組", "🏷️ 分類管理", "📊 使用統計", "⚙️ 系統設定"])
        
        with tab1:
            self._show_template_groups_tab()
        with tab2:
            self._show_category_management_tab()
        with tab3:
            self._show_usage_statistics_tab()
        with tab4:
            self._show_system_settings_tab()
    
    def _show_template_groups_tab(self):
        """顯示範本群組管理頁籤"""
        st.markdown("### 📂 範本群組管理")
        st.info("💡 將相關的範本組織成群組，便於批量比對和管理")
        
        # 獲取所有範本
        templates = self.system.get_templates_list()
        if not templates:
            st.warning("⚠️ 尚未建立任何範本，請先到「PDF變數標記」頁面上傳範本。")
            return
        
        # 初始化群組資料
        if 'template_groups' not in st.session_state:
            st.session_state.template_groups = {}
        
        # 顯示現有群組
        st.markdown("#### 📋 現有群組")
        
        groups = st.session_state.template_groups
        if groups:
            for group_name, group_data in groups.items():
                with st.expander(f"📁 {group_name} ({len(group_data.get('templates', []))} 個範本)"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**描述：** {group_data.get('description', '無描述')}")
                        st.write(f"**建立時間：** {group_data.get('created_at', '未知')}")
                        
                        # 顯示群組中的範本
                        group_templates = group_data.get('templates', [])
                        if group_templates:
                            st.write("**包含的範本：**")
                            for template_id in group_templates:
                                template = next((t for t in templates if t['id'] == template_id), None)
                                if template:
                                    st.write(f"- {template['name']}")
                        else:
                            st.write("*此群組尚未包含任何範本*")
                    
                    with col2:
                        if st.button(f"🗑️ 刪除群組", key=f"delete_group_{group_name}"):
                            del st.session_state.template_groups[group_name]
                            st.success(f"✅ 群組 '{group_name}' 已刪除")
                            st.rerun()
        else:
            st.info("📝 尚未建立任何範本群組")
        
        # 建立新群組
        st.markdown("#### ➕ 建立新群組")
        
        with st.form("create_group_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                group_name = st.text_input("群組名稱", placeholder="例如：保險申請表群組")
                group_description = st.text_area("群組描述", placeholder="描述此群組的用途...")
            
            with col2:
                # 選擇要加入群組的範本
                template_options = [f"{t['name']} (ID: {t['id']})" for t in templates]
                selected_templates = st.multiselect(
                    "選擇範本",
                    template_options,
                    help="選擇要加入此群組的範本"
                )
            
            submitted = st.form_submit_button("🚀 建立群組", use_container_width=True)
            
            if submitted and group_name:
                if group_name in st.session_state.template_groups:
                    st.error(f"❌ 群組名稱 '{group_name}' 已存在")
                else:
                    # 提取範本ID
                    template_ids = []
                    for template_option in selected_templates:
                        template_id = int(template_option.split("ID: ")[1].split(")")[0])
                        template_ids.append(template_id)
                    
                    # 建立群組
                    st.session_state.template_groups[group_name] = {
                        'description': group_description,
                        'templates': template_ids,
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'usage_count': 0
                    }
                    
                    st.success(f"✅ 群組 '{group_name}' 建立成功！")
                    st.rerun()
            elif submitted:
                st.error("❌ 請填寫群組名稱")
    
    def _show_category_management_tab(self):
        """顯示分類管理頁籤"""
        st.markdown("### 🏷️ 分類管理")
        st.info("💡 為範本建立分類標籤，便於組織和搜尋")
        
        # 預定義分類
        default_categories = [
            "📋 申請表單",
            "📝 合約文件", 
            "📊 報告範本",
            "💰 財務文件",
            "🏢 公司文件",
            "📞 聯絡表單",
            "⚖️ 法律文件",
            "🔧 其他"
        ]
        
        # 初始化分類資料
        if 'template_categories' not in st.session_state:
            st.session_state.template_categories = {cat: [] for cat in default_categories}
        
        # 獲取所有範本
        templates = self.system.get_templates_list()
        if not templates:
            st.warning("⚠️ 尚未建立任何範本")
            return
        
        # 顯示分類統計
        st.markdown("#### 📊 分類統計")
        
        categories = st.session_state.template_categories
        col_count = 4
        cols = st.columns(col_count)
        
        for i, (category, template_ids) in enumerate(categories.items()):
            with cols[i % col_count]:
                st.metric(category, len(template_ids))
        
        # 範本分類管理
        st.markdown("#### 🏷️ 範本分類")
        
        for template in templates:
            template_id = template['id']
            template_name = template['name']
            
            with st.expander(f"📄 {template_name}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # 顯示目前分類
                    current_categories = []
                    for category, template_ids in categories.items():
                        if template_id in template_ids:
                            current_categories.append(category)
                    
                    if current_categories:
                        st.write(f"**目前分類：** {', '.join(current_categories)}")
                    else:
                        st.write("**目前分類：** 未分類")
                    
                    # 選擇新分類
                    new_categories = st.multiselect(
                        "選擇分類",
                        default_categories,
                        default=current_categories,
                        key=f"categories_{template_id}"
                    )
                
                with col2:
                    if st.button(f"💾 更新", key=f"update_cat_{template_id}"):
                        # 先從所有分類中移除此範本
                        for category in categories:
                            if template_id in categories[category]:
                                categories[category].remove(template_id)
                        
                        # 加入新分類
                        for category in new_categories:
                            if template_id not in categories[category]:
                                categories[category].append(template_id)
                        
                        st.success("✅ 分類已更新")
                        st.rerun()
    
    def _show_usage_statistics_tab(self):
        """顯示使用統計頁籤"""
        st.markdown("### 📊 使用統計分析")
        
        templates = self.system.get_templates_list()
        if not templates:
            st.warning("⚠️ 尚未建立任何範本")
            return
        
        # 模擬使用統計資料
        st.markdown("#### 📈 範本使用統計")
        
        # 建立統計表格
        stats_data = []
        for template in templates:
            template_id = template['id']
            annotations = self.system.get_template_annotations(template_id)
            
            # 模擬使用次數（在實際應用中，這應該從資料庫或日誌中獲取）
            import random
            usage_count = random.randint(0, 50)
            last_used = template.get('updated_at', '未知')
            
            stats_data.append({
                '範本名稱': template['name'],
                '變數數量': len(annotations),
                '使用次數': usage_count,
                '建立時間': template.get('created_at', '未知'),
                '最後使用': last_used,
                '狀態': '活躍' if usage_count > 10 else '較少使用'
            })
        
        # 顯示統計表格
        if stats_data:
            df = pd.DataFrame(stats_data)
            st.dataframe(df, use_container_width=True)
            
            # 顯示統計圖表
            st.markdown("#### 📊 使用趨勢")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 使用次數分布
                st.bar_chart(df.set_index('範本名稱')['使用次數'])
            
            with col2:
                # 變數數量分布
                st.bar_chart(df.set_index('範本名稱')['變數數量'])
    
    def _show_system_settings_tab(self):
        """顯示系統設定頁籤"""
        st.markdown("### ⚙️ 系統設定")
        
        # 一般設定
        st.markdown("#### 🔧 一般設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_backup = st.checkbox("自動備份", value=True, help="自動備份範本和資料")
            show_tooltips = st.checkbox("顯示提示", value=True, help="在介面中顯示操作提示")
            dark_mode = st.checkbox("深色模式", value=False, help="使用深色主題")
        
        with col2:
            max_file_size = st.slider("最大檔案大小 (MB)", 1, 100, 50)
            backup_frequency = st.selectbox("備份頻率", ["每日", "每週", "每月"])
            language = st.selectbox("語言", ["繁體中文", "簡體中文", "English"])
        
        # 比對設定
        st.markdown("#### 🔍 比對設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_similarity = st.slider("預設相似度閾值 (%)", 50, 95, 80)
            strict_mode_default = st.checkbox("預設嚴格模式", value=True)
        
        with col2:
            max_comparison_files = st.number_input("最大比對檔案數", 1, 20, 5)
            enable_parallel_processing = st.checkbox("啟用並行處理", value=True)
        
        # 儲存設定
        if st.button("💾 儲存設定", use_container_width=True, type="primary"):
            # TODO: 實際儲存設定到配置檔案
            settings = {
                'auto_backup': auto_backup,
                'show_tooltips': show_tooltips,
                'dark_mode': dark_mode,
                'max_file_size': max_file_size,
                'backup_frequency': backup_frequency,
                'language': language,
                'default_similarity': default_similarity,
                'strict_mode_default': strict_mode_default,
                'max_comparison_files': max_comparison_files,
                'enable_parallel_processing': enable_parallel_processing
            }
            
            st.session_state['system_settings'] = settings
            st.success("✅ 設定已儲存！")
        
        # 資料管理
        st.markdown("#### 🗄️ 資料管理")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📤 匯出資料", use_container_width=True):
                st.info("🚧 匯出功能正在開發中...")
        
        with col2:
            if st.button("📥 匯入資料", use_container_width=True):
                st.info("🚧 匯入功能正在開發中...")
        
        with col3:
            if st.button("🧹 清理快取", use_container_width=True):
                # 清理session state中的快取資料
                cache_keys = [key for key in st.session_state.keys() if 'cache' in key]
                for key in cache_keys:
                    del st.session_state[key]
                st.success("✅ 快取已清理")

def template_settings_page():
    """範本管理設定頁面入口"""
    settings = TemplateSettings()
    settings.show_template_settings()

if __name__ == "__main__":
    template_settings_page()