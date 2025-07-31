# 檔名: core/pdf_annotation_system.py
# (已加入刪除單筆標記功能的最終完整版本)

import streamlit as st
import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple
from PIL import Image
from io import BytesIO

try:
    from pdf2image import convert_from_bytes
except ImportError:
    st.error("缺少 pdf2image 套件，請執行 pip install pdf2image")
try:
    import fitz
except ImportError:
    st.error("缺少 PyMuPDF 套件，請執行 pip install PyMuPDF")

# Poppler path - 雲端環境自適應
POPPLER_PATH = None  # 讓雲端環境自動尋找，本地環境可手動指定

class PDFAnnotationSystem:
    def __init__(self, db_path="data/pdf_annotations.db"):
        self.db_path = db_path
        self.templates_dir = "data/pdf_templates"
        os.makedirs(self.templates_dir, exist_ok=True)
        self.setup_database()
    
    def setup_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL,
                        description TEXT, total_pages INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS page_types (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_id INTEGER,
                        page_number INTEGER,
                        page_type TEXT DEFAULT '變數頁面', -- '變數頁面' or '參考資料'
                        note TEXT DEFAULT '', -- 頁面備註說明
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (template_id) REFERENCES templates (id) ON DELETE CASCADE,
                        UNIQUE(template_id, page_number)
                    )
                ''')
                
                # 檢查是否需要添加note欄位（為了向後相容）
                cursor.execute("PRAGMA table_info(page_types)")
                columns = [column[1] for column in cursor.fetchall()]
                if 'note' not in columns:
                    cursor.execute("ALTER TABLE page_types ADD COLUMN note TEXT DEFAULT ''")
                if 'updated_at' not in columns:
                    cursor.execute("ALTER TABLE page_types ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS annotations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, template_id INTEGER,
                        page_number INTEGER, variable_name TEXT, variable_type TEXT,
                        x_start REAL, y_start REAL, x_end REAL, y_end REAL,
                        sample_value TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (template_id) REFERENCES templates (id) ON DELETE CASCADE
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS variable_database (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, variable_name TEXT UNIQUE NOT NULL,
                        variable_type TEXT, sample_values TEXT, usage_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
        except Exception as e:
            st.error(f"資料庫初始化錯誤：{str(e)}")
    
    def convert_pdf_to_images(self, pdf_file) -> List[Image.Image]:
        try:
            pdf_file.seek(0)
            pdf_bytes = pdf_file.read()
            try:
                images = convert_from_bytes(pdf_bytes, dpi=200, fmt='PNG', poppler_path=POPPLER_PATH)
                st.info("✅ 使用 pdf2image 成功轉換 PDF。")
                return images
            except Exception:
                # 雲端環境通常沒有 poppler，直接使用 PyMuPDF
                st.info("🔄 使用 PyMuPDF 轉換 PDF...")
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                images = [Image.frombytes("RGB", [p.get_pixmap(dpi=200).width, p.get_pixmap(dpi=200).height], p.get_pixmap(dpi=200).samples) for p in doc]
                doc.close()
                st.info("✅ PDF 轉換成功。")
                return images
        except Exception as e:
            st.error(f"所有 PDF 轉換方法均失敗：{str(e)}")
            return []

    def save_template(self, name: str, description: str, pdf_file, images: List[Image.Image]) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO templates (name, description, total_pages, updated_at) VALUES (?, ?, ?, ?)",
                    (name, description, len(images), datetime.now())
                )
                template_id = cursor.lastrowid
            pdf_file.seek(0)
            with open(os.path.join(self.templates_dir, f"{template_id}_original.pdf"), 'wb') as f:
                f.write(pdf_file.read())
            for i, image in enumerate(images):
                image.save(os.path.join(self.templates_dir, f"{template_id}_page_{i+1}.png"), "PNG")
            return template_id
        except sqlite3.IntegrityError:
             st.error(f"範本儲存錯誤：範本名稱 '{name}' 已存在。")
             return -1
        except Exception as e:
            st.error(f"範本儲存錯誤：{str(e)}")
            return -1

    def get_templates_list(self) -> List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM templates ORDER BY updated_at DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            st.error(f"取得範本列表錯誤：{str(e)}")
            return []
    
    def get_template_info(self, template_id: int) -> Dict:
        """獲取單個範本的詳細資訊"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            st.error(f"取得範本資訊錯誤：{str(e)}")
            return None
    
    def load_template_page(self, template_id: int, page_number: int) -> Image.Image:
        image_path = os.path.join(self.templates_dir, f"{template_id}_page_{page_number}.png")
        return Image.open(image_path) if os.path.exists(image_path) else None

    def save_annotation(self, template_id: int, page_number: int, variable_name: str, variable_type: str, coordinates: Tuple[float, float, float, float], sample_value: str = ""):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                x_start, y_start, x_end, y_end = coordinates
                cursor.execute(
                    "INSERT INTO annotations (template_id, page_number, variable_name, variable_type, x_start, y_start, x_end, y_end, sample_value) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (template_id, page_number, variable_name, variable_type, x_start, y_start, x_end, y_end, sample_value)
                )
                self.update_variable_database(cursor, variable_name, variable_type, sample_value)
            return True
        except Exception as e:
            st.error(f"儲存標記錯誤：{str(e)}")
            return False

    def update_variable_database(self, cursor: sqlite3.Cursor, variable_name: str, variable_type: str, sample_value: str):
        cursor.execute("SELECT id, sample_values, usage_count FROM variable_database WHERE variable_name = ?", (variable_name,))
        result = cursor.fetchone()
        if result:
            var_id, existing_samples, usage_count = result
            samples_list = json.loads(existing_samples) if existing_samples else []
            if sample_value and sample_value not in samples_list:
                samples_list.append(sample_value)
            cursor.execute(
                "UPDATE variable_database SET sample_values = ?, usage_count = ?, updated_at = ? WHERE id = ?",
                (json.dumps(samples_list, ensure_ascii=False), usage_count + 1, datetime.now(), var_id)
            )
        else:
            samples_list = [sample_value] if sample_value else []
            cursor.execute(
                "INSERT INTO variable_database (variable_name, variable_type, sample_values, usage_count) VALUES (?, ?, ?, ?)",
                (variable_name, variable_type, json.dumps(samples_list, ensure_ascii=False), 1)
            )

    def get_variable_database(self) -> List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM variable_database ORDER BY usage_count DESC, variable_name")
                db_list = []
                for row in cursor.fetchall():
                    item = dict(row)
                    item['sample_values'] = json.loads(item['sample_values']) if item['sample_values'] else []
                    db_list.append(item)
                return db_list
        except Exception as e:
            st.error(f"取得變數資料庫錯誤：{str(e)}")
            return []

    def get_template_annotations(self, template_id: int, page_number: int = None) -> List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                query = "SELECT * FROM annotations WHERE template_id = ?"
                params = [template_id]
                if page_number is not None:
                    query += " AND page_number = ?"
                    params.append(page_number)
                cursor.execute(query, tuple(params))
                annotations = [dict(row) for row in cursor.fetchall()]
                for ann in annotations:
                    ann['coordinates'] = (ann['x_start'], ann['y_start'], ann['x_end'], ann['y_end'])
                return annotations
        except Exception as e:
            st.error(f"取得標記資訊錯誤：{str(e)}")
            return []

    def delete_template(self, template_id: int, total_pages: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))
            
            pdf_path = os.path.join(self.templates_dir, f"{template_id}_original.pdf")
            if os.path.exists(pdf_path): os.remove(pdf_path)
            
            for i in range(1, total_pages + 1):
                img_path = os.path.join(self.templates_dir, f"{template_id}_page_{i}.png")
                if os.path.exists(img_path): os.remove(img_path)
            
            return True
        except Exception as e:
            st.error(f"刪除範本時發生錯誤：{e}")
            return False

    # --- 【新增功能】 ---
    def delete_annotation(self, annotation_id: int) -> bool:
        """刪除單筆變數標記"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 在刪除前，先取得變數名稱，以便更新 variable_database
                cursor.execute("SELECT variable_name FROM annotations WHERE id = ?", (annotation_id,))
                result = cursor.fetchone()
                if result:
                    variable_name = result[0]
                    # 刪除標記
                    cursor.execute("DELETE FROM annotations WHERE id = ?", (annotation_id,))
                    # 更新 variable_database 的 usage_count
                    cursor.execute(
                        "UPDATE variable_database SET usage_count = usage_count - 1 WHERE variable_name = ?",
                        (variable_name,)
                    )
            return True
        except Exception as e:
            st.error(f"刪除標記時發生錯誤：{e}")
            return False

    def update_annotation(self, annotation_id: int, variable_name: str, variable_type: str, 
                         coordinates: tuple, sample_value: str = "") -> bool:
        """更新變數標記"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                x_start, y_start, x_end, y_end = coordinates
                cursor.execute(
                    """UPDATE annotations 
                       SET variable_name = ?, variable_type = ?, 
                           x_start = ?, y_start = ?, x_end = ?, y_end = ?, 
                           sample_value = ?
                       WHERE id = ?""",
                    (variable_name, variable_type, x_start, y_start, x_end, y_end, sample_value, annotation_id)
                )
                # 更新變數資料庫
                self.update_variable_database(cursor, variable_name, variable_type, sample_value)
            return True
        except Exception as e:
            st.error(f"更新標記時發生錯誤：{e}")
            return False
    
    def set_page_type(self, template_id: int, page_number: int, page_type: str, note: str = "") -> bool:
        """設定頁面類型 ('變數頁面' 或 '參考資料') 和備註"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT OR REPLACE INTO page_types (template_id, page_number, page_type, note, updated_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (template_id, page_number, page_type, note, datetime.now())
                )
            return True
        except Exception as e:
            st.error(f"設定頁面類型時發生錯誤：{e}")
            return False
    
    def get_page_type(self, template_id: int, page_number: int) -> str:
        """取得頁面類型"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT page_type FROM page_types WHERE template_id = ? AND page_number = ?",
                    (template_id, page_number)
                )
                result = cursor.fetchone()
                return result[0] if result else '變數頁面'  # 預設為變數頁面
        except Exception as e:
            st.error(f"取得頁面類型時發生錯誤：{e}")
            return '變數頁面'
    
    def get_page_info(self, template_id: int, page_number: int) -> tuple:
        """取得頁面類型和備註"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT page_type, note FROM page_types WHERE template_id = ? AND page_number = ?",
                    (template_id, page_number)
                )
                result = cursor.fetchone()
                if result:
                    return result[0], result[1]
                else:
                    return '變數頁面', ''  # 預設為變數頁面，無備註
        except Exception as e:
            st.error(f"取得頁面資訊時發生錯誤：{e}")
            return '變數頁面', ''
    
    def get_template_page_types(self, template_id: int) -> dict:
        """取得範本所有頁面的類型"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT page_number, page_type FROM page_types WHERE template_id = ?",
                    (template_id,)
                )
                return {row[0]: row[1] for row in cursor.fetchall()}
        except Exception as e:
            st.error(f"取得頁面類型時發生錯誤：{e}")
            return {}
    
    def get_template_page_info(self, template_id: int) -> dict:
        """取得範本所有頁面的詳細資訊（類型和備註）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT page_number, page_type, note FROM page_types WHERE template_id = ?",
                    (template_id,)
                )
                return {row[0]: {'type': row[1], 'note': row[2]} for row in cursor.fetchall()}
        except Exception as e:
            st.error(f"取得頁面資訊時發生錯誤：{e}")
            return {}