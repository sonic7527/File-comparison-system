#!/usr/bin/env python3
"""
清理所有範本和資料庫記錄的腳本
"""

import os
import sqlite3
import shutil
from pathlib import Path

def clean_all_templates():
    """清理所有範本和資料庫記錄"""
    
    # 獲取專案根目錄
    root_dir = Path(__file__).parent
    
    print("🧹 開始清理所有範本...")
    
    # 1. 清理本地資料庫
    db_path = root_dir / "data" / "templates.db"
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 刪除所有範本群組
            cursor.execute("DELETE FROM template_groups")
            print(f"✅ 已刪除所有範本群組")
            
            # 刪除所有範本檔案
            cursor.execute("DELETE FROM template_files")
            print(f"✅ 已刪除所有範本檔案")
            
            # 刪除所有比對範本
            cursor.execute("DELETE FROM comparison_templates")
            print(f"✅ 已刪除所有比對範本")
            
            conn.commit()
            conn.close()
            print(f"✅ 本地資料庫已清理完成")
        except Exception as e:
            print(f"❌ 清理本地資料庫失敗: {e}")
    
    # 2. 清理上傳目錄
    upload_dirs = [
        root_dir / "uploads",
        root_dir / "data" / "templates",
        root_dir / "data" / "comparison_templates",
        root_dir / "data" / "excel_templates",
        root_dir / "data" / "pdf_templates",
        root_dir / "generated_files"
    ]
    
    for upload_dir in upload_dirs:
        if upload_dir.exists():
            try:
                shutil.rmtree(upload_dir)
                print(f"✅ 已刪除目錄: {upload_dir}")
            except Exception as e:
                print(f"❌ 刪除目錄失敗 {upload_dir}: {e}")
    
    # 3. 重新創建必要的目錄
    for upload_dir in upload_dirs:
        try:
            upload_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 已重新創建目錄: {upload_dir}")
        except Exception as e:
            print(f"❌ 創建目錄失敗 {upload_dir}: {e}")
    
    # 4. 清理雲端資料庫（如果可用）
    try:
        import streamlit as st
        from core.turso_database import turso_db
        
        if turso_db.is_cloud_mode():
            # 獲取所有比對範本
            templates = turso_db.get_comparison_templates()
            for template in templates:
                turso_db.delete_comparison_template(template['id'])
            print(f"✅ 雲端資料庫已清理完成")
        else:
            print(f"⚠️ 雲端資料庫未連接，跳過清理")
    except Exception as e:
        print(f"❌ 清理雲端資料庫失敗: {e}")
    
    print("\n🎉 清理完成！所有範本和資料庫記錄已刪除")
    print("💡 現在可以重新測試上傳功能")

if __name__ == "__main__":
    clean_all_templates() 