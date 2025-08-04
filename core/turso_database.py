import os
import streamlit as st
from typing import List, Dict, Optional
import tempfile
import shutil
from pathlib import Path
import asyncio
import json
from libsql_client import create_client

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
            
            # 如果無法從 secrets 獲取，嘗試從環境變數獲取
            if not turso_url:
                turso_url = os.environ.get("TURSO_URL")
            if not turso_token:
                turso_token = os.environ.get("TURSO_TOKEN")
            
            if turso_url and turso_token:
                # 延遲創建客戶端，避免在初始化時就觸發異步問題
                self.turso_url = turso_url
                self.turso_token = turso_token
                self.client = None  # 暫時設為 None，在需要時才創建
                # 移除初始化時的消息顯示，避免在啟動時就顯示
            else:
                # 移除初始化時的消息顯示，避免在啟動時就顯示
                self.client = None
        except Exception as e:
            # 移除初始化時的消息顯示，避免在啟動時就顯示
            self.client = None
    
    def is_cloud_mode(self) -> bool:
        """檢查是否為雲端模式"""
        try:
            return (hasattr(self, 'turso_url') and 
                   hasattr(self, 'turso_token') and 
                   self.turso_url and 
                   self.turso_token and
                   isinstance(self.turso_url, str) and
                   isinstance(self.turso_token, str))
        except Exception:
            return False
    
    def is_configured(self) -> bool:
        """檢查是否已配置 Turso"""
        return self.is_cloud_mode()
    
    def check_and_display_status(self):
        """檢查並顯示 Turso 狀態"""
        if self.is_cloud_mode():
            st.success("✅ Turso 雲端資料庫已配置")
        else:
            st.warning("⚠️ 未配置 Turso，將使用本地 SQLite")
            st.info("💡 如需使用雲端資料庫，請在 Streamlit Cloud 中配置 Turso secrets")
    
    def _ensure_client(self):
        """確保客戶端已創建"""
        if self.client is None and self.is_cloud_mode():
            try:
                import concurrent.futures
                import asyncio
                
                async def create_client_async():
                    return create_client(
                        url=self.turso_url,
                        auth_token=self.turso_token
                    )
                
                def create_client_safe():
                    return asyncio.run(create_client_async())
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(create_client_safe)
                    self.client = future.result(timeout=10)
                
                st.success("✅ Turso 客戶端創建成功")
                return True
            except Exception as e:
                st.warning(f"⚠️ Turso 客戶端創建失敗：{str(e)}")
                return False
        return self.client is not None
    
    def _execute_async(self, async_func):
        """執行異步操作的通用方法"""
        try:
            import concurrent.futures
            import asyncio
            
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(async_func())
                finally:
                    loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async)
                return future.result(timeout=10)
        except Exception as e:
            st.error(f"異步操作失敗：{str(e)}")
            return None

    def create_tables(self):
        """創建必要的表格"""
        if not self.is_cloud_mode():
            return
        
        try:
            # 創建所有必要的表格
            tables_sql = [
                """CREATE TABLE IF NOT EXISTS comparison_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );""",
                """CREATE TABLE IF NOT EXISTS template_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    source_excel_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );""",
                """CREATE TABLE IF NOT EXISTS template_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES template_groups (id) ON DELETE CASCADE
                );""",
                """CREATE TABLE IF NOT EXISTS field_definitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    default_value TEXT,
                    description TEXT,
                    dropdown_options TEXT,
                    sort_order INTEGER,
                    FOREIGN KEY (group_id) REFERENCES template_groups (id) ON DELETE CASCADE
                );"""
            ]
            
            async def async_create():
                client = create_client(
                    url=self.turso_url,
                    auth_token=self.turso_token
                )
                for sql in tables_sql:
                    await client.execute(sql)
                await client.close()
            
            self._execute_async(async_create)
            return True
        except Exception as e:
            st.error(f"創建表格失敗: {str(e)}")
            return False
    
    def get_comparison_templates(self) -> List[Dict]:
        """獲取所有比對範本"""
        if not self.is_cloud_mode():
            return []
        
        try:
            async def async_get():
                client = create_client(
                    url=self.turso_url,
                    auth_token=self.turso_token
                )
                result = await client.execute("SELECT * FROM comparison_templates ORDER BY created_at DESC")
                await client.close()
                return result.rows
            
            rows = self._execute_async(async_get)
            if rows is None:
                return []
            
            templates = []
            for row in rows:
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
            
            async def async_save():
                client = create_client(
                    url=self.turso_url,
                    auth_token=self.turso_token
                )
                result = await client.execute(sql, [name, filename, filepath, file_type, file_size])
                await client.close()
                return result.last_insert_rowid
            
            template_id = self._execute_async(async_save)
            if template_id is not None:
                return template_id
            else:
                return -1
        except Exception as e:
            st.error(f"保存範本錯誤：{str(e)}")
            return -1
    
    def delete_comparison_template(self, template_id: int) -> bool:
        """刪除比對範本"""
        if not self.is_cloud_mode():
            return False
        
        try:
            sql = "DELETE FROM comparison_templates WHERE id = ?"
            
            async def async_delete():
                client = create_client(
                    url=self.turso_url,
                    auth_token=self.turso_token
                )
                await client.execute(sql, [template_id])
                await client.close()
                return True
            
            result = self._execute_async(async_delete)
            return result is not None
        except Exception as e:
            st.error(f"刪除範本錯誤：{str(e)}")
            return False

    # 智能文件生成系統的雲端操作方法
    def create_template_group_cloud(self, name: str, source_excel_path: str, field_definitions: List[Dict], template_files: List[Dict]) -> int:
        """創建範本群組到雲端"""
        if not self.is_cloud_mode():
            return -1
        
        try:
            async def async_create_group():
                client = create_client(
                    url=self.turso_url,
                    auth_token=self.turso_token
                )
                
                # 1. 插入範本群組
                result = await client.execute(
                    "INSERT INTO template_groups (name, source_excel_path) VALUES (?, ?)",
                    [name, source_excel_path]
                )
                group_id = result.last_insert_rowid
                
                # 2. 插入欄位定義
                for i, field in enumerate(field_definitions):
                    dropdown_json = json.dumps(field.get('dropdown_options', []))
                    await client.execute(
                        """
                        INSERT INTO field_definitions (group_id, name, default_value, description, dropdown_options, sort_order)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        [group_id, field['name'], field.get('default_value', ''), field.get('description', ''), dropdown_json, i]
                    )
                
                # 3. 插入範本檔案
                for file_info in template_files:
                    await client.execute(
                        """
                        INSERT INTO template_files (group_id, filename, filepath, file_type, file_size)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        [group_id, file_info['filename'], file_info['filepath'], file_info['file_type'], file_info['file_size']]
                    )
                
                await client.close()
                return group_id
            
            group_id = self._execute_async(async_create_group)
            return group_id if group_id is not None else -1
        except Exception as e:
            st.error(f"創建範本群組錯誤：{str(e)}")
            return -1

    def get_all_template_groups_cloud(self) -> List[Dict]:
        """獲取所有範本群組"""
        if not self.is_cloud_mode():
            return []
        
        try:
            async def async_get_groups():
                client = create_client(
                    url=self.turso_url,
                    auth_token=self.turso_token
                )
                result = await client.execute("SELECT * FROM template_groups ORDER BY created_at DESC")
                await client.close()
                return result.rows
            
            rows = self._execute_async(async_get_groups)
            if rows is None:
                return []
            
            groups = []
            for row in rows:
                group = {
                    'id': row[0],
                    'name': row[1],
                    'source_excel_path': row[2],
                    'created_at': row[3]
                }
                groups.append(group)
            return groups
        except Exception as e:
            st.error(f"獲取範本群組錯誤：{str(e)}")
            return []

    def get_template_files_cloud(self, group_id: int) -> List[Dict]:
        """獲取範本群組的檔案"""
        if not self.is_cloud_mode():
            return []
        
        try:
            async def async_get_files():
                client = create_client(
                    url=self.turso_url,
                    auth_token=self.turso_token
                )
                result = await client.execute("SELECT * FROM template_files WHERE group_id = ? ORDER BY created_at DESC", [group_id])
                await client.close()
                return result.rows
            
            rows = self._execute_async(async_get_files)
            if rows is None:
                return []
            
            files = []
            for row in rows:
                file_info = {
                    'id': row[0],
                    'group_id': row[1],
                    'filename': row[2],
                    'filepath': row[3],
                    'file_type': row[4],
                    'file_size': row[5],
                    'created_at': row[6]
                }
                files.append(file_info)
            return files
        except Exception as e:
            st.error(f"獲取範本檔案錯誤：{str(e)}")
            return []

    def get_field_definitions_cloud(self, group_id: int) -> List[Dict]:
        """獲取範本群組的欄位定義"""
        if not self.is_cloud_mode():
            return []
        
        try:
            async def async_get_fields():
                client = create_client(
                    url=self.turso_url,
                    auth_token=self.turso_token
                )
                result = await client.execute(
                    "SELECT * FROM field_definitions WHERE group_id = ? ORDER BY sort_order",
                    [group_id]
                )
                fields = []
                for row in result.rows:
                    field = {
                        'id': row[0],
                        'group_id': row[1],
                        'name': row[2],
                        'default_value': row[3],
                        'description': row[4],
                        'dropdown_options': json.loads(row[5]) if row[5] else [],
                        'sort_order': row[6]
                    }
                    fields.append(field)
                await client.close()
                return fields
            
            fields = self._execute_async(async_get_fields)
            return fields if fields is not None else []
        except Exception as e:
            st.error(f"獲取欄位定義錯誤：{str(e)}")
            return []

    def delete_template_file_cloud(self, file_id: int) -> bool:
        """刪除雲端範本檔案"""
        if not self.is_cloud_mode():
            return False
        
        try:
            async def async_delete_file():
                client = create_client(
                    url=self.turso_url,
                    auth_token=self.turso_token
                )
                await client.execute("DELETE FROM template_files WHERE id = ?", [file_id])
                await client.close()
                return True
            
            result = self._execute_async(async_delete_file)
            return result is not None
        except Exception as e:
            st.error(f"刪除範本檔案錯誤：{str(e)}")
            return False

    def add_template_file_cloud(self, group_id: int, file_info: Dict) -> bool:
        """添加範本檔案到雲端"""
        if not self.is_cloud_mode():
            return False
        
        try:
            async def async_add_file():
                client = create_client(
                    url=self.turso_url,
                    auth_token=self.turso_token
                )
                await client.execute(
                    """
                    INSERT INTO template_files (group_id, filename, filepath, file_type, file_size)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [group_id, file_info['filename'], file_info['filepath'], file_info['file_type'], file_info['file_size']]
                )
                await client.close()
                return True
            
            result = self._execute_async(async_add_file)
            return result is not None
        except Exception as e:
            st.error(f"添加範本檔案錯誤：{str(e)}")
            return False

    def delete_template_group_cloud(self, group_id: int) -> bool:
        """刪除雲端範本群組"""
        if not self.is_cloud_mode():
            return False
        
        try:
            async def async_delete_group():
                client = create_client(
                    url=self.turso_url,
                    auth_token=self.turso_token
                )
                # 先刪除相關的檔案和欄位定義
                await client.execute("DELETE FROM template_files WHERE group_id = ?", [group_id])
                await client.execute("DELETE FROM field_definitions WHERE group_id = ?", [group_id])
                # 最後刪除群組
                await client.execute("DELETE FROM template_groups WHERE id = ?", [group_id])
                await client.close()
                return True
            
            result = self._execute_async(async_delete_group)
            return result is not None
        except Exception as e:
            st.error(f"刪除範本群組錯誤：{str(e)}")
            return False

# 移除全局實例化，改為在需要時創建實例 