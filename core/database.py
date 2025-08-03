import sqlite3
import os
import json
from typing import List, Dict
from pathlib import Path
import streamlit as st

# --- 這是我們之前修正好的正確路徑設定 ---
ROOT_DIR = Path(__file__).parent.parent 
DB_PATH = ROOT_DIR / "data" / "templates.db"
# -----------------------------------------

def get_db_connection():
    """建立並返回資料庫連線，啟用外鍵約束"""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_database():
    """初始化資料庫和表格"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # 建立範本群組表格
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS template_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            source_excel_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        # 建立範本檔案表格
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS template_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            file_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES template_groups (id) ON DELETE CASCADE
        );
        """)
        # 建立欄位定義表格
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS field_definitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            default_value TEXT,
            description TEXT,
            dropdown_options TEXT, -- 儲存為 JSON 字串
            sort_order INTEGER,
            FOREIGN KEY (group_id) REFERENCES template_groups (id) ON DELETE CASCADE
        );
        """)
        # 建立比對範本表格
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comparison_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()

def create_template_group(name: str, source_excel_path: str, field_definitions: List[Dict], template_files: List[str]):
    """一次性創建範本群組、欄位定義和範本檔案紀錄"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            # 1. 插入範本群組
            cursor.execute("INSERT INTO template_groups (name, source_excel_path) VALUES (?, ?)", (name, source_excel_path))
            group_id = cursor.lastrowid
            # 2. 插入欄位定義
            for i, field in enumerate(field_definitions):
                dropdown_json = json.dumps(field.get('dropdown_options', []))
                cursor.execute(
                    """
                    INSERT INTO field_definitions (group_id, name, default_value, description, dropdown_options, sort_order)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (group_id, field['name'], field.get('default_value', ''), field.get('description', ''), dropdown_json, i)
                )
            # 3. 插入範本檔案
            for file_path in template_files:
                filename = os.path.basename(file_path)
                file_type = os.path.splitext(filename)[1].lower().replace('.', '')
                cursor.execute(
                    "INSERT INTO template_files (group_id, filename, filepath, file_type) VALUES (?, ?, ?, ?)",
                    (group_id, filename, file_path, file_type)
                )
            conn.commit()
            return group_id
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError(f"名為 '{name}' 的範本群組已存在。")
        except Exception as e:
            conn.rollback()
            raise e

def get_all_template_groups() -> List[Dict]:
    """獲取所有範本群組及其檔案計數，並包含 source_excel_path (已修正)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                tg.id, 
                tg.name, 
                tg.source_excel_path, -- 已加入此欄位
                (SELECT COUNT(*) FROM template_files tf WHERE tf.group_id = tg.id) as file_count
            FROM template_groups tg
            ORDER BY tg.created_at DESC;
        """)
        groups = [dict(row) for row in cursor.fetchall()]
        return groups

def get_template_files(group_id: int) -> List[Dict]:
    """根據群組ID獲取所有範本檔案"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, filename, filepath, file_type FROM template_files WHERE group_id = ?", (group_id,))
        files = [dict(row) for row in cursor.fetchall()]
        return files

def get_field_definitions(group_id: int) -> List[Dict]:
    """根據群組ID獲取所有欄位定義"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, default_value, description, dropdown_options FROM field_definitions WHERE group_id = ? ORDER BY sort_order", (group_id,))
        fields = []
        for row in cursor.fetchall():
            field = dict(row)
            # 將 JSON 字串解析回 list
            field['dropdown_options'] = json.loads(field['dropdown_options']) if field['dropdown_options'] else []
            fields.append(field)
        return fields

def update_field_definitions(group_id: int, fields: List[Dict]) -> bool:
    """更新指定群組的欄位定義"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            # 刪除舊的定義
            cursor.execute("DELETE FROM field_definitions WHERE group_id = ?", (group_id,))
            # 插入新的定義
            for i, field in enumerate(fields):
                dropdown_json = json.dumps(field.get('dropdown_options', []))
                cursor.execute(
                    """
                    INSERT INTO field_definitions (group_id, name, default_value, description, dropdown_options, sort_order)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (group_id, field['name'], field.get('default_value', ''), field.get('description', ''), dropdown_json, i)
                )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

def delete_template_file(file_id: int) -> bool:
    """刪除單一範本檔案（物理檔案和資料庫紀錄）"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT filepath FROM template_files WHERE id = ?", (file_id,))
            row = cursor.fetchone()
            if row:
                if os.path.exists(row['filepath']):
                    os.remove(row['filepath'])
                cursor.execute("DELETE FROM template_files WHERE id = ?", (file_id,))
                conn.commit()
                return True
        except Exception:
            conn.rollback()
    return False

def delete_template_group(group_id: int) -> bool:
    """刪除整個範本群組（包含所有檔案和欄位定義）"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            # 1. 刪除實體檔案
            cursor.execute("SELECT filepath FROM template_files WHERE group_id = ?", (group_id,))
            for row in cursor.fetchall():
                if os.path.exists(row['filepath']):
                    os.remove(row['filepath'])
            
            cursor.execute("SELECT source_excel_path FROM template_groups WHERE id = ?", (group_id,))
            row = cursor.fetchone()
            if row and os.path.exists(row['source_excel_path']):
                os.remove(row['source_excel_path'])

            # 2. 刪除資料庫紀錄 (由於設定了 ON DELETE CASCADE，會自動刪除關聯的檔案和欄位)
            cursor.execute("DELETE FROM template_groups WHERE id = ?", (group_id,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
    return False

def update_template_group_fields(group_id: int) -> List[Dict]:
    """
    重新解析基本資料Excel檔案的欄位
    只解析基本資料檔案，不影響其他範本檔案
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 獲取群組的基本資料Excel路徑
            cursor.execute("SELECT source_excel_path FROM template_groups WHERE id = ?", (group_id,))
            result = cursor.fetchone()
            if not result:
                return None
            
            excel_path = result['source_excel_path']
            # 使用 pathlib 來組合和檢查路徑
            full_excel_path = ROOT_DIR / excel_path
            if not full_excel_path.exists():
                return None
            
            # 重新解析Excel檔案
            import pandas as pd
            df = pd.read_excel(full_excel_path, header=None)
            
            # 提取欄位定義
            field_definitions = []
            for index, row in df.iterrows():
                if index == 0:
                    continue
                
                field_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None
                if not field_name or field_name == 'nan':
                    continue

                field_value = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                description = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                
                # 處理下拉選單選項
                dropdown_options = []
                if "這邊可以做成下拉式選單" in description:
                    clean_desc = description.replace("這邊可以做成下拉式選單", "").strip()
                    options = [opt.strip() for opt in clean_desc.split('\n') if opt.strip()]
                    if len(options) <= 1:
                        import re
                        options = re.split(r'\d+\.|\d+\s', clean_desc)
                        options = [opt.strip() for opt in options if opt.strip()]
                    if options:
                        dropdown_options = options
                
                field_definitions.append({
                    'name': field_name,
                    'default_value': field_value,
                    'description': description,
                    'dropdown_options': dropdown_options
                })
            
            # 更新資料庫中的欄位定義
            if update_field_definitions(group_id, field_definitions):
                return field_definitions
            else:
                return None
                    
    except Exception as e:
        print(f"重新解析欄位時發生錯誤: {str(e)}")
        return None
