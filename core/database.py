import os
import json
import sqlite3
from typing import List, Dict
from pathlib import Path

# --- 本地 SQLite 資料庫設定 ---
ROOT_DIR = Path(__file__).parent.parent
DB_PATH = ROOT_DIR / "data" / "templates.db"

def get_db_connection():
    """建立並返回本地 SQLite 資料庫連線，啟用外鍵約束"""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_database():
    """初始化本地 SQLite 資料庫和表格"""
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
            file_size INTEGER DEFAULT 0,
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
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                cursor.execute(
                    "INSERT INTO template_files (group_id, filename, filepath, file_type, file_size) VALUES (?, ?, ?, ?, ?)",
                    (group_id, filename, file_path, file_type, file_size)
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
        cursor.execute("SELECT id, filename, filepath, file_type, file_size FROM template_files WHERE group_id = ?", (group_id,))
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
            
            # 2. 刪除資料庫紀錄（外鍵約束會自動處理相關紀錄）
            cursor.execute("DELETE FROM template_groups WHERE id = ?", (group_id,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

def update_template_group_fields(group_id: int) -> List[Dict]:
    """獲取指定群組的欄位定義（用於編輯）"""
    return get_field_definitions(group_id)

# --- 比對範本相關函數 ---
def get_comparison_templates() -> List[Dict]:
    """獲取所有比對範本"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM comparison_templates ORDER BY created_at DESC")
        templates = [dict(row) for row in cursor.fetchall()]
        return templates

def save_comparison_template(name: str, filename: str, filepath: str, file_type: str, file_size: int) -> int:
    """保存比對範本"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO comparison_templates (name, filename, filepath, file_type, file_size) VALUES (?, ?, ?, ?, ?)",
                (name, filename, filepath, file_type, file_size)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError(f"名為 '{name}' 的比對範本已存在。")
        except Exception as e:
            conn.rollback()
            raise e

def delete_comparison_template(template_id: int) -> bool:
    """刪除比對範本"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            # 先獲取檔案路徑
            cursor.execute("SELECT filepath FROM comparison_templates WHERE id = ?", (template_id,))
            row = cursor.fetchone()
            if row:
                # 刪除實體檔案
                if os.path.exists(row['filepath']):
                    os.remove(row['filepath'])
                # 刪除資料庫紀錄
                cursor.execute("DELETE FROM comparison_templates WHERE id = ?", (template_id,))
                conn.commit()
                return True
        except Exception:
            conn.rollback()
    return False

def add_template_file(group_id: int, file_info: Dict) -> bool:
    """添加範本檔案到指定群組"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO template_files (group_id, filename, filepath, file_type, file_size) VALUES (?, ?, ?, ?, ?)",
                (group_id, file_info['filename'], file_info['filepath'], file_info['file_type'], file_info.get('file_size', 0))
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False 