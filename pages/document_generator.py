import streamlit as st
import pandas as pd
import os
import sqlite3
from typing import Dict, List, Any
from datetime import datetime
import json
from PIL import Image
import io
import base64

class DocumentGenerator:
    def __init__(self):
        self.templates_dir = "data/document_templates"
        self.db_path = "data/document_templates.db"
        self.generated_dir = "generated_files"
        self._ensure_directories()
        self._init_database()
    
    def _ensure_directories(self):
        """確保必要的目錄存在"""
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.generated_dir, exist_ok=True)
    
    def _init_database(self):
        """初始化資料庫 - 支援群組化管理"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 基本資料群組表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS field_groups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        category TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 基本資料欄位表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS field_definitions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_id INTEGER,
                        field_name TEXT NOT NULL,
                        field_description TEXT,
                        field_type TEXT DEFAULT 'text',
                        sample_value TEXT,
                        is_required BOOLEAN DEFAULT 1,
                        display_order INTEGER DEFAULT 0,
                        FOREIGN KEY (group_id) REFERENCES field_groups (id)
                    )
                """)
                
                # 範本群組表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS template_groups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        field_group_id INTEGER,
                        name TEXT NOT NULL,
                        description TEXT,
                        template_type TEXT,
                        page_size TEXT DEFAULT 'A4',
                        page_orientation TEXT DEFAULT 'PORTRAIT',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (field_group_id) REFERENCES field_groups (id)
                    )
                """)
                
                # 範本文件表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS template_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_group_id INTEGER,
                        file_name TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        file_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (template_group_id) REFERENCES template_groups (id)
                    )
                """)
                
                conn.commit()
        except Exception as e:
            st.error(f"❌ 資料庫初始化失敗：{str(e)}")
    
    def create_field_group(self, name: str, description: str, category: str = "一般") -> int:
        """創建基本資料群組"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO field_groups (name, description, category)
                    VALUES (?, ?, ?)
                """, (name, description, category))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            st.error(f"❌ 創建基本資料群組失敗：{str(e)}")
            return None
    
    def add_field_definition(self, group_id: int, field_name: str, field_description: str, 
                           field_type: str = "text", sample_value: str = "", 
                           is_required: bool = True, display_order: int = 0):
        """添加欄位定義到群組"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO field_definitions 
                    (group_id, field_name, field_description, field_type, sample_value, is_required, display_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (group_id, field_name, field_description, field_type, sample_value, is_required, display_order))
                conn.commit()
                return True
        except Exception as e:
            st.error(f"❌ 添加欄位定義失敗：{str(e)}")
            return False
    
    def get_all_field_groups(self) -> List[Dict]:
        """獲取所有基本資料群組"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT fg.*, COUNT(fd.id) as field_count
                    FROM field_groups fg
                    LEFT JOIN field_definitions fd ON fg.id = fd.group_id
                    GROUP BY fg.id
                    ORDER BY fg.created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            st.error(f"❌ 獲取基本資料群組失敗：{str(e)}")
            return []
    
    def get_field_group_details(self, group_id: int) -> Dict:
        """獲取基本資料群組詳細資訊"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 獲取群組資訊
                cursor.execute("SELECT * FROM field_groups WHERE id = ?", (group_id,))
                group = cursor.fetchone()
                if not group:
                    return None
                
                # 獲取欄位定義
                cursor.execute("""
                    SELECT * FROM field_definitions 
                    WHERE group_id = ? 
                    ORDER BY display_order, field_name
                """, (group_id,))
                fields = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'group': dict(group),
                    'fields': fields
                }
        except Exception as e:
            st.error(f"❌ 獲取群組詳細資訊失敗：{str(e)}")
            return None
    
    def create_template_group(self, field_group_id: int, name: str, description: str, 
                            template_type: str, page_size: str = "A4", 
                            orientation: str = "PORTRAIT") -> int:
        """創建範本群組"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO template_groups 
                    (field_group_id, name, description, template_type, page_size, page_orientation)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (field_group_id, name, description, template_type, page_size, orientation))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            st.error(f"❌ 創建範本群組失敗：{str(e)}")
            return None
    
    def add_template_file(self, template_group_id: int, file_name: str, file_path: str, file_type: str):
        """添加範本文件"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO template_files 
                    (template_group_id, file_name, file_path, file_type)
                    VALUES (?, ?, ?, ?)
                """, (template_group_id, file_name, file_path, file_type))
                conn.commit()
                return True
        except Exception as e:
            st.error(f"❌ 添加範本文件失敗：{str(e)}")
            return False
    
    def get_all_template_groups(self) -> List[Dict]:
        """獲取所有範本群組"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT tg.*, fg.name as field_group_name, fg.description as field_group_description,
                           COUNT(tf.id) as file_count
                    FROM template_groups tg
                    LEFT JOIN field_groups fg ON tg.field_group_id = fg.id
                    LEFT JOIN template_files tf ON tg.id = tf.template_group_id
                    GROUP BY tg.id
                    ORDER BY tg.created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            st.error(f"❌ 獲取範本群組失敗：{str(e)}")
            return []
    
    def get_template_group_details(self, template_group_id: int) -> Dict:
        """獲取範本群組詳細資訊"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 獲取範本群組資訊
                cursor.execute("""
                    SELECT tg.*, fg.name as field_group_name, fg.description as field_group_description
                    FROM template_groups tg
                    LEFT JOIN field_groups fg ON tg.field_group_id = fg.id
                    WHERE tg.id = ?
                """, (template_group_id,))
                template_group = cursor.fetchone()
                if not template_group:
                    return None
                
                # 獲取範本文件
                cursor.execute("""
                    SELECT * FROM template_files 
                    WHERE template_group_id = ?
                    ORDER BY created_at DESC
                """, (template_group_id,))
                files = [dict(row) for row in cursor.fetchall()]
                
                # 獲取對應的基本資料群組
                field_group_details = self.get_field_group_details(template_group['field_group_id'])
                
                return {
                    'template_group': dict(template_group),
                    'files': files,
                    'field_group': field_group_details
                }
        except Exception as e:
            st.error(f"❌ 獲取範本群組詳細資訊失敗：{str(e)}")
            return None
    
    def convert_image_to_excel(self, image_path: str, output_path: str, page_size: str = "A4", orientation: str = "PORTRAIT"):
        """將圖片轉換為A4格式的Excel文件"""
        try:
            st.info("✅ 開始轉換圖片為Excel格式")
            
            # 讀取圖片
            with Image.open(image_path) as img:
                # 獲取圖片尺寸
                img_width, img_height = img.size
                
                # A4尺寸設定（以點為單位）
                if orientation == "LANDSCAPE":
                    page_width = 29.7 * 28.35  # A4橫式寬度
                    page_height = 21.0 * 28.35  # A4橫式高度
                else:
                    page_width = 21.0 * 28.35   # A4直式寬度
                    page_height = 29.7 * 28.35  # A4直式高度
                
                # 計算縮放比例
                scale_x = page_width / img_width
                scale_y = page_height / img_height
                scale = min(scale_x, scale_y)  # 保持比例
                
                # 調整圖片尺寸
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 創建Excel文件
                from openpyxl import Workbook
                from openpyxl.drawing.image import Image as XLImage
                
                wb = Workbook()
                ws = wb.active
                
                # 設定頁面大小
                ws.page_setup.paperSize = ws.page_setup.PAPERSIZE_A4
                if orientation == "LANDSCAPE":
                    ws.page_setup.orientation = ws.page_setup.ORIENTATION_LANDSCAPE
                
                # 將圖片保存為臨時文件
                temp_img_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                img_resized.save(temp_img_path)
                
                # 插入圖片到Excel
                xl_img = XLImage(temp_img_path)
                ws.add_image(xl_img, 'A1')
                
                # 調整欄寬和行高以適應圖片
                ws.column_dimensions['A'].width = new_width / 7
                ws.row_dimensions[1].height = new_height * 0.75
                
                # 保存Excel文件
                wb.save(output_path)
                
                # 清理臨時文件
                os.remove(temp_img_path)
                
                st.success(f"✅ 圖片已轉換為A4 {orientation}格式的Excel文件")
                return output_path
                
        except Exception as e:
            st.error(f"❌ 圖片轉Excel失敗：{str(e)}")
            return None
    
    def convert_image_to_word(self, image_path: str, output_path: str, page_size: str = "A4", orientation: str = "PORTRAIT"):
        """將圖片轉換為A4格式的Word文件"""
        try:
            st.info("✅ 開始轉換圖片為Word格式")
            
            from docx import Document
            from docx.shared import Inches, Cm
            from docx.enum.section import WD_ORIENT
            
            # 創建Word文件
            doc = Document()
            
            # 設定A4頁面大小
            section = doc.sections[0]
            if orientation == "LANDSCAPE":
                section.orientation = WD_ORIENT.LANDSCAPE
                section.page_width = Cm(29.7)
                section.page_height = Cm(21.0)
            else:
                section.page_width = Cm(21.0)
                section.page_height = Cm(29.7)
            
            # 讀取圖片
            with Image.open(image_path) as img:
                # 獲取圖片尺寸
                img_width, img_height = img.size
                
                # 計算A4尺寸（以英寸為單位）
                if orientation == "LANDSCAPE":
                    page_width_inch = 29.7 / 2.54
                    page_height_inch = 21.0 / 2.54
                else:
                    page_width_inch = 21.0 / 2.54
                    page_height_inch = 29.7 / 2.54
                
                # 計算縮放比例
                scale_x = page_width_inch / (img_width / 96)
                scale_y = page_height_inch / (img_height / 96)
                scale = min(scale_x, scale_y)
                
                # 調整圖片尺寸
                new_width = img_width * scale
                new_height = img_height * scale
                
                # 將圖片保存為臨時文件
                temp_img_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                img_resized = img.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)
                img_resized.save(temp_img_path)
                
                # 插入圖片到Word
                doc.add_picture(temp_img_path, width=Inches(new_width / 96), height=Inches(new_height / 96))
                
                # 清理臨時文件
                os.remove(temp_img_path)
            
            # 保存Word文件
            doc.save(output_path)
            
            st.success(f"✅ 圖片已轉換為A4 {orientation}格式的Word文件")
            return output_path
            
        except Exception as e:
            st.error(f"❌ 圖片轉Word失敗：{str(e)}")
            return None
    
    def generate_document_from_template(self, template_group_id: int, input_data: Dict, output_name: str) -> str:
        """從範本群組生成文件"""
        try:
            template_details = self.get_template_group_details(template_group_id)
            if not template_details:
                st.error("❌ 找不到範本群組資訊")
                return None
            
            template_group = template_details['template_group']
            files = template_details['files']
            
            if not files:
                st.error("❌ 範本群組中沒有文件")
                return None
            
            # 使用第一個文件作為範本
            template_file = files[0]
            template_path = os.path.join(self.templates_dir, template_file['file_path'])
            
            if not os.path.exists(template_path):
                st.error(f"❌ 範本文件不存在：{template_path}")
                return None
            
            # 根據文件類型處理
            if template_group['template_type'].lower() == 'excel':
                return self._generate_excel_document(template_path, input_data, output_name)
            elif template_group['template_type'].lower() == 'word':
                return self._generate_word_document(template_path, input_data, output_name)
            else:
                st.error(f"❌ 不支援的文件類型：{template_group['template_type']}")
                return None
                
        except Exception as e:
            st.error(f"❌ 生成文件失敗：{str(e)}")
            return None
    
    def _generate_excel_document(self, template_path: str, input_data: Dict, output_name: str) -> str:
        """生成Excel文件"""
        try:
            st.info("✅ 複製Excel模板")
            
            import shutil
            output_path = os.path.join(self.generated_dir, f"{output_name}.xlsx")
            shutil.copy2(template_path, output_path)
            
            # 使用openpyxl填入資料
            try:
                from openpyxl import load_workbook
                workbook = load_workbook(output_path, data_only=False, keep_vba=False)
                
                filled_count = 0
                for sheet in workbook.sheetnames:
                    sheet_obj = workbook[sheet]
                    st.info(f"✅ 處理工作表：{sheet}")
                    
                    for row in sheet_obj.iter_rows():
                        for cell in row:
                            if cell.value:
                                cell_value_str = str(cell.value).strip()
                                # 檢查是否在輸入資料中有對應的欄位
                                for field_name, value in input_data.items():
                                    if cell_value_str == field_name.strip():
                                        cell.value = value
                                        filled_count += 1
                                        st.info(f"✅ 填入 {field_name}: {value}")
                                        break
                
                workbook.save(output_path)
                st.success(f"✅ 成功填入 {filled_count} 個欄位")
                return output_path
                
            except Exception as e:
                st.warning(f"⚠️ openpyxl處理失敗：{str(e)}")
                return None
                
        except Exception as e:
            st.error(f"❌ Excel生成失敗：{str(e)}")
            return None
    
    def _generate_word_document(self, template_path: str, input_data: Dict, output_name: str) -> str:
        """生成Word文件"""
        try:
            st.info("✅ 複製Word模板")
            
            import shutil
            output_path = os.path.join(self.generated_dir, f"{output_name}.docx")
            shutil.copy2(template_path, output_path)
            
            # 使用python-docx填入資料
            try:
                from docx import Document
                doc = Document(output_path)
                
                filled_count = 0
                for paragraph in doc.paragraphs:
                    for field_name, value in input_data.items():
                        if field_name in paragraph.text:
                            paragraph.text = paragraph.text.replace(field_name, str(value))
                            filled_count += 1
                            st.info(f"✅ 填入 {field_name}: {value}")
                
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for field_name, value in input_data.items():
                                if field_name in cell.text:
                                    cell.text = cell.text.replace(field_name, str(value))
                                    filled_count += 1
                                    st.info(f"✅ 填入 {field_name}: {value}")
                
                doc.save(output_path)
                st.success(f"✅ 成功填入 {filled_count} 個欄位")
                return output_path
                
            except ImportError:
                st.error("❌ 需要安裝 python-docx：pip install python-docx")
                return None
            except Exception as e:
                st.warning(f"⚠️ Word處理失敗：{str(e)}")
                return None
                
        except Exception as e:
            st.error(f"❌ Word生成失敗：{str(e)}")
            return None

def document_generator_tab():
    """文件生成頁面 - 群組化管理版本"""
    st.header("📄 智能文件生成系統")
    
    generator = DocumentGenerator()
    
    # 創建標籤頁
    tab1, tab2, tab3, tab4 = st.tabs(["📋 基本資料群組", "📤 範本群組", "📝 生成文件", "📊 管理面板"])
    
    with tab1:
        st.subheader("📋 基本資料群組管理")
        st.markdown("""
        **概念說明：**
        - **基本資料群組**：定義一組固定的輸入欄位（如：申請表基本資料）
        - **欄位定義**：每個群組包含多個欄位（姓名、地址、電話等）
        - **重複使用**：同一組基本資料可以用於生成不同格式的文件
        """)
        
        # 創建新群組
        with st.expander("➕ 創建新的基本資料群組"):
            with st.form("create_field_group"):
                group_name = st.text_input("群組名稱", help="例如：申請表基本資料")
                group_description = st.text_area("群組說明", help="描述這個群組的用途")
                group_category = st.selectbox("分類", ["申請表", "報表", "證明文件", "其他"])
                
                if st.form_submit_button("📋 創建群組"):
                    if group_name and group_description:
                        group_id = generator.create_field_group(group_name, group_description, group_category)
                        if group_id:
                            st.success(f"✅ 群組創建成功！ID: {group_id}")
                            st.session_state['new_group_id'] = group_id
                    else:
                        st.warning("⚠️ 請填寫群組名稱和說明")
        
        # 添加欄位定義
        if 'new_group_id' in st.session_state:
            with st.expander("📝 添加欄位定義"):
                st.info(f"正在為群組 ID: {st.session_state['new_group_id']} 添加欄位")
                
                with st.form("add_field_definition"):
                    field_name = st.text_input("欄位名稱", help="例如：申請人姓名")
                    field_description = st.text_area("欄位說明", help="描述這個欄位的用途")
                    field_type = st.selectbox("資料類型", ["text", "number", "date", "email", "phone"])
                    sample_value = st.text_input("範例值", help="提供範例值")
                    is_required = st.checkbox("必填欄位", value=True)
                    display_order = st.number_input("顯示順序", value=0, min_value=0)
                    
                    if st.form_submit_button("➕ 添加欄位"):
                        if field_name:
                            success = generator.add_field_definition(
                                st.session_state['new_group_id'], field_name, field_description,
                                field_type, sample_value, is_required, display_order
                            )
                            if success:
                                st.success(f"✅ 欄位 '{field_name}' 添加成功！")
                        else:
                            st.warning("⚠️ 請輸入欄位名稱")
        
        # 顯示現有群組
        st.subheader("📋 現有基本資料群組")
        field_groups = generator.get_all_field_groups()
        
        if field_groups:
            for group in field_groups:
                with st.expander(f"📋 {group['name']} ({group['field_count']} 個欄位)"):
                    st.write(f"**說明：** {group['description']}")
                    st.write(f"**分類：** {group['category']}")
                    st.write(f"**創建時間：** {group['created_at']}")
                    
                    # 顯示欄位詳情
                    details = generator.get_field_group_details(group['id'])
                    if details and details['fields']:
                        st.write("**欄位列表：**")
                        for field in details['fields']:
                            st.write(f"- {field['field_name']}: {field['field_description']} ({field['field_type']})")
        else:
            st.info("📝 還沒有創建任何基本資料群組")
    
    with tab2:
        st.subheader("📤 範本群組管理")
        st.markdown("""
        **概念說明：**
        - **範本群組**：基於基本資料群組創建的不同格式範本
        - **文件格式**：可以是Excel、Word或圖片轉換的文件
        - **A4格式**：自動轉換為A4直式或橫式格式
        """)
        
        # 創建新範本群組
        with st.expander("➕ 創建新的範本群組"):
            field_groups = generator.get_all_field_groups()
            if not field_groups:
                st.warning("⚠️ 請先創建基本資料群組")
            else:
                with st.form("create_template_group"):
                    # 選擇基本資料群組
                    field_group_options = {f"{g['name']} - {g['description']}": g['id'] for g in field_groups}
                    selected_field_group = st.selectbox(
                        "選擇基本資料群組",
                        list(field_group_options.keys()),
                        help="選擇要基於哪個基本資料群組創建範本"
                    )
                    
                    template_name = st.text_input("範本群組名稱", help="例如：申請表Excel版本")
                    template_description = st.text_area("範本說明", help="描述這個範本的用途")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        template_type = st.selectbox("文件類型", ["Excel", "Word"])
                        page_orientation = st.selectbox(
                            "頁面方向",
                            ["PORTRAIT", "LANDSCAPE"],
                            format_func=lambda x: "直式" if x == "PORTRAIT" else "橫式"
                        )
                    
                    with col2:
                        # 支援圖片文件上傳
                        if template_type == "Excel":
                            template_file = st.file_uploader(
                                "範本文件 (Excel或圖片)",
                                type=['xlsx', 'xls', 'png', 'jpg', 'jpeg', 'gif', 'bmp'],
                                help="上傳Excel文件或圖片文件（會自動轉換為A4格式）"
                            )
                        else:
                            template_file = st.file_uploader(
                                "範本文件 (Word或圖片)",
                                type=['docx', 'doc', 'png', 'jpg', 'jpeg', 'gif', 'bmp'],
                                help="上傳Word文件或圖片文件（會自動轉換為A4格式）"
                            )
                    
                    if st.form_submit_button("📤 創建範本群組"):
                        if selected_field_group and template_name and template_file:
                            field_group_id = field_group_options[selected_field_group]
                            
                            # 創建範本群組
                            template_group_id = generator.create_template_group(
                                field_group_id, template_name, template_description,
                                template_type, "A4", page_orientation
                            )
                            
                            if template_group_id:
                                # 處理文件上傳
                                file_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                
                                if template_file.type.startswith('image/'):
                                    st.info("✅ 檢測到圖片文件，正在轉換...")
                                    
                                    # 保存原始圖片
                                    temp_img_path = os.path.join(generator.templates_dir, f"temp_{file_timestamp}.png")
                                    with open(temp_img_path, "wb") as f:
                                        f.write(template_file.getvalue())
                                    
                                    # 轉換圖片
                                    if template_type == "Excel":
                                        final_path = os.path.join(generator.templates_dir, f"template_{file_timestamp}.xlsx")
                                        success = generator.convert_image_to_excel(temp_img_path, final_path, "A4", page_orientation)
                                    else:
                                        final_path = os.path.join(generator.templates_dir, f"template_{file_timestamp}.docx")
                                        success = generator.convert_image_to_word(temp_img_path, final_path, "A4", page_orientation)
                                    
                                    # 清理臨時文件
                                    os.remove(temp_img_path)
                                    
                                    if success:
                                        file_name = os.path.basename(final_path)
                                        generator.add_template_file(template_group_id, file_name, file_name, template_type)
                                        st.success("✅ 範本群組創建成功！")
                                    else:
                                        st.error("❌ 圖片轉換失敗")
                                else:
                                    # 直接保存文件
                                    file_name = f"template_{file_timestamp}.{template_type.lower()}"
                                    final_path = os.path.join(generator.templates_dir, file_name)
                                    
                                    with open(final_path, "wb") as f:
                                        f.write(template_file.getvalue())
                                    
                                    generator.add_template_file(template_group_id, file_name, file_name, template_type)
                                    st.success("✅ 範本群組創建成功！")
                        else:
                            st.warning("⚠️ 請填寫所有必要欄位")
        
        # 顯示現有範本群組
        st.subheader("📤 現有範本群組")
        template_groups = generator.get_all_template_groups()
        
        if template_groups:
            for group in template_groups:
                with st.expander(f"📤 {group['name']} ({group['file_count']} 個文件)"):
                    st.write(f"**說明：** {group['description']}")
                    st.write(f"**基本資料群組：** {group['field_group_name']}")
                    st.write(f"**文件類型：** {group['template_type']}")
                    st.write(f"**頁面方向：** {'直式' if group['page_orientation'] == 'PORTRAIT' else '橫式'}")
                    st.write(f"**創建時間：** {group['created_at']}")
        else:
            st.info("📝 還沒有創建任何範本群組")
    
    with tab3:
        st.subheader("📝 生成文件")
        st.markdown("""
        **使用流程：**
        1. 選擇範本群組
        2. 系統自動載入對應的基本資料輸入頁面
        3. 填入新資料
        4. 生成新文件
        """)
        
        template_groups = generator.get_all_template_groups()
        if not template_groups:
            st.warning("⚠️ 請先創建範本群組")
            return
        
        # 選擇範本群組
        template_options = {f"{g['name']} - {g['field_group_name']}": g['id'] for g in template_groups}
        selected_template_name = st.selectbox(
            "選擇範本群組",
            list(template_options.keys()),
            help="選擇要使用的範本群組"
        )
        
        if selected_template_name:
            template_group_id = template_options[selected_template_name]
            
            # 獲取範本詳細資訊
            template_details = generator.get_template_group_details(template_group_id)
            
            if template_details and template_details['field_group']:
                field_group = template_details['field_group']
                fields = field_group['fields']
                
                st.success(f"✅ 載入基本資料群組：{field_group['group']['name']}")
                st.info(f"📋 發現 {len(fields)} 個輸入欄位")
                
                # 顯示輸入欄位
                st.subheader("📝 輸入資料")
                
                input_data = {}
                for i, field in enumerate(fields):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        if field['field_type'] == 'number':
                            value = st.number_input(
                                f"{field['field_name']}",
                                value=float(field['sample_value']) if field['sample_value'] and str(field['sample_value']).replace('.', '').isdigit() else 0.0,
                                key=f"input_{i}",
                                help=field['field_description']
                            )
                        elif field['field_type'] == 'date':
                            value = st.date_input(
                                f"{field['field_name']}",
                                key=f"input_{i}",
                                help=field['field_description']
                            )
                        else:
                            value = st.text_input(
                                f"{field['field_name']}",
                                value=str(field['sample_value']) if field['sample_value'] else "",
                                key=f"input_{i}",
                                help=field['field_description']
                            )
                    
                    with col2:
                        st.write(f"**說明：** {field['field_description']}")
                        if field['is_required']:
                            st.write("**必填**")
                    
                    input_data[field['field_name']] = value
                
                # 生成文件
                st.subheader("🚀 生成文件")
                
                col1, col2 = st.columns(2)
                with col1:
                    output_name = st.text_input(
                        "輸出文件名稱",
                        value=f"生成文件_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        help="不需要輸入副檔名"
                    )
                
                with col2:
                    if st.button("🚀 生成文件", type="primary"):
                        if output_name:
                            with st.spinner("正在生成文件..."):
                                output_path = generator.generate_document_from_template(template_group_id, input_data, output_name)
                                
                                if output_path and os.path.exists(output_path):
                                    st.success("✅ 文件生成成功！")
                                    
                                    # 提供下載連結
                                    with open(output_path, "rb") as f:
                                        file_data = f.read()
                                    
                                    file_extension = os.path.splitext(output_path)[1]
                                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if file_extension == ".xlsx" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                    
                                    st.download_button(
                                        label="📥 下載文件",
                                        data=file_data,
                                        file_name=f"{output_name}{file_extension}",
                                        mime=mime_type
                                    )
                                    
                                    st.info(f"📁 文件已儲存至：{output_path}")
                                else:
                                    st.error("❌ 文件生成失敗")
                        else:
                            st.warning("⚠️ 請輸入輸出文件名稱")
            else:
                st.warning("⚠️ 無法載入範本詳細資訊")
    
    with tab4:
        st.subheader("📊 管理面板")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📋 基本資料群組", len(generator.get_all_field_groups()))
            st.metric("📤 範本群組", len(generator.get_all_template_groups()))
        
        with col2:
            st.metric("📄 生成文件", len(os.listdir(generator.generated_dir)) if os.path.exists(generator.generated_dir) else 0)
            st.metric("✅ 系統狀態", "正常運行")

if __name__ == "__main__":
    document_generator_tab() 