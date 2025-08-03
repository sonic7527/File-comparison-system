import os
import streamlit as st
from typing import List, Dict, Optional
from libsql_client import create_client
import tempfile
import shutil
from pathlib import Path

class TursoDatabase:
    """Turso 雲端資料庫管理類"""
    
    def __init__(self):
        self.client = None
        self._init_turso()
    
    def _init_turso(self):
        """初始化 Turso 連接"""
        try:
            # 從 Streamlit secrets 獲取配置
            turso_url = st.secrets.get("turso", {}).get("url")
            turso_token = st.secrets.get("turso", {}).get("token")
            
            if turso_url and turso_token:
                self.client = create_client(
                    url=turso_url,
                    auth_token=turso_token
                )
                st.success("✅ 已連接到 Turso 雲端資料庫")
            else:
                st.warning("⚠️ 未配置 Turso，將使用本地 SQLite")
                self.client = None
        except Exception as e:
            st.error(f"❌ Turso 連接失敗：{str(e)}")
            self.client = None
    
    def is_cloud_mode(self) -> bool:
        """檢查是否為雲端模式"""
        return self.client is not None
    
    def create_tables(self):
        """創建必要的表格"""
        if not self.is_cloud_mode():
            return
        
        try:
            # 創建 comparison_templates 表格
            sql = """
            CREATE TABLE IF NOT EXISTS comparison_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            self.client.execute(sql)
            st.success("✅ Turso 表格創建成功")
        except Exception as e:
            st.error(f"❌ 創建表格失敗：{str(e)}")
    
    def get_comparison_templates(self) -> List[Dict]:
        """獲取所有比對範本"""
        if not self.is_cloud_mode():
            return []
        
        try:
            result = self.client.execute("SELECT * FROM comparison_templates ORDER BY created_at DESC")
            templates = []
            for row in result.rows:
                template = {
                    'id': row[0],
                    'name': row[1],
                    'filename': row[2],
                    'filepath': row[3],
                    'file_type': row[4],
                    'file_size': row[5],
                    'created_at': row[6]
                }
                templates.append(template)
            return templates
        except Exception as e:
            st.error(f"獲取範本列表錯誤：{str(e)}")
            return []
    
    def save_comparison_template(self, name: str, filename: str, filepath: str, file_type: str, file_size: int) -> int:
        """保存比對範本"""
        if not self.is_cloud_mode():
            return -1
        
        try:
            sql = """
            INSERT INTO comparison_templates (name, filename, filepath, file_type, file_size)
            VALUES (?, ?, ?, ?, ?)
            """
            result = self.client.execute(sql, [name, filename, filepath, file_type, file_size])
            return result.last_insert_rowid
        except Exception as e:
            st.error(f"保存範本錯誤：{str(e)}")
            return -1
    
    def delete_comparison_template(self, template_id: int) -> bool:
        """刪除比對範本"""
        if not self.is_cloud_mode():
            return False
        
        try:
            sql = "DELETE FROM comparison_templates WHERE id = ?"
            self.client.execute(sql, [template_id])
            return True
        except Exception as e:
            st.error(f"刪除範本錯誤：{str(e)}")
            return False

# 全局實例
turso_db = TursoDatabase() 