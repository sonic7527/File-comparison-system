import sqlite3
import os
import json
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 資料庫路徑
DB_PATH = "data/templates.db"

def init_database():
    """初始化資料庫，並設定外鍵約束"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS template_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                excel_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS template_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_type TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES template_groups (id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS field_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER UNIQUE,
                field_data TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES template_groups (id) ON DELETE CASCADE
            )
        ''')
        conn.commit()

def create_template_group(name, excel_path, field_data):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO template_groups (name, excel_path) VALUES (?, ?)", (name, excel_path))
        group_id = cursor.lastrowid
        cursor.execute("INSERT INTO field_definitions (group_id, field_data) VALUES (?, ?)", (group_id, json.dumps(field_data, ensure_ascii=False)))
        conn.commit()
        return group_id

def add_template_file(group_id, filename, filepath, file_type):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO template_files (group_id, filename, filepath, file_type) VALUES (?, ?, ?, ?)", (group_id, filename, filepath, file_type))
        conn.commit()

def get_all_template_groups():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT tg.*, COUNT(tf.id) as file_count
            FROM template_groups tg
            LEFT JOIN template_files tf ON tg.id = tf.group_id
            GROUP BY tg.id
            ORDER BY tg.created_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

def get_template_files(group_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM template_files WHERE group_id = ?", (group_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_field_definitions(group_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT field_data FROM field_definitions WHERE group_id = ?", (group_id,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else []

def delete_template_file(file_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM template_files WHERE id = ?", (file_id,))
            result = cursor.fetchone()
            if result:
                filepath = result[0]
                if os.path.exists(filepath):
                    os.remove(filepath)
                cursor.execute("DELETE FROM template_files WHERE id = ?", (file_id,))
                conn.commit()
                return True
    except sqlite3.Error as e:
        logging.error(f"刪除檔案時發生資料庫錯誤: {e}")
    return False

def delete_template_group(group_id):
    """
    修正後的刪除函式，加入更強的錯誤處理和獨立的資料庫連線。
    """
    # 獲取所有檔案路徑 (在資料庫交易外)
    try:
        conn_for_select = sqlite3.connect(DB_PATH)
        cursor_for_select = conn_for_select.cursor()
        cursor_for_select.execute("SELECT filepath FROM template_files WHERE group_id = ?", (group_id,))
        files_to_delete = cursor_for_select.fetchall()
        cursor_for_select.execute("SELECT excel_path FROM template_groups WHERE id = ?", (group_id,))
        excel_path_tuple = cursor_for_select.fetchone()
        conn_for_select.close() # 立刻關閉連線
    except sqlite3.Error as e:
        logging.error(f"刪除前獲取檔案路徑失敗: {e}")
        return False

    # 刪除實體檔案
    try:
        for file_path_tuple in files_to_delete:
            if os.path.exists(file_path_tuple[0]):
                os.remove(file_path_tuple[0])
                logging.info(f"已刪除實體檔案: {file_path_tuple[0]}")
        
        if excel_path_tuple and os.path.exists(excel_path_tuple[0]):
            os.remove(excel_path_tuple[0])
            logging.info(f"已刪除來源Excel: {excel_path_tuple[0]}")
    except OSError as e:
        logging.error(f"刪除實體檔案時發生錯誤 (可能檔案被佔用): {e}")
        return False

    # 刪除資料庫記錄
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("DELETE FROM template_groups WHERE id = ?", (group_id,))
            conn.commit()
            logging.info(f"已成功從資料庫刪除群組 ID: {group_id} 及其關聯記錄。")
            return True
    except sqlite3.Error as e:
        logging.error(f"刪除群組時發生資料庫錯誤: {e}")
        return False


def update_field_definitions(group_id, field_data):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE field_definitions SET field_data = ? WHERE group_id = ?",
            (json.dumps(field_data, ensure_ascii=False), group_id)
        )
        conn.commit()