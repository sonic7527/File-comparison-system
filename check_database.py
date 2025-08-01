import sqlite3
import os

DB_PATH = "data/excel_templates.db"

def check_database():
    """檢查資料庫內容"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            print("=== Excel範本資料庫檢查結果 ===")
            
            # 檢查所有表格
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"表格列表: {[table['name'] for table in tables]}")
            
            # 檢查範本群組
            cursor.execute("SELECT * FROM template_groups")
            groups = cursor.fetchall()
            print(f"\n範本群組數量: {len(groups)}")
            for group in groups:
                print(f"群組ID: {group['id']}, 名稱: {group['name']}, 類型: {group.get('template_type', 'unknown')}")
            
            # 檢查範本文件
            cursor.execute("SELECT * FROM template_files")
            files = cursor.fetchall()
            print(f"\n範本文件數量: {len(files)}")
            for file in files:
                print(f"文件ID: {file['id']}, 名稱: {file['file_name']}, 類型: {file.get('file_type', 'unknown')}, 路徑: {file['file_path']}")
            
            # 檢查欄位定義
            cursor.execute("SELECT * FROM field_definitions")
            fields = cursor.fetchall()
            print(f"\n欄位定義數量: {len(fields)}")
            for field in fields:
                print(f"欄位ID: {field['id']}, 名稱: {field['field_name']}, 描述: {field['field_description']}")
            
            # 檢查欄位群組
            cursor.execute("SELECT * FROM field_groups")
            field_groups = cursor.fetchall()
            print(f"\n欄位群組數量: {len(field_groups)}")
            for fg in field_groups:
                print(f"群組ID: {fg['id']}, 名稱: {fg['name']}, 描述: {fg['description']}")
                
    except Exception as e:
        print(f"檢查資料庫時發生錯誤: {str(e)}")

if __name__ == "__main__":
    check_database() 