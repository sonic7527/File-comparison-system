import os
import base64
import streamlit as st
from typing import Optional, Dict, List
from pathlib import Path
import tempfile
import shutil

class GitHubStorage:
    """GitHub 檔案存儲管理類"""
    
    def __init__(self):
        self.github_token = None
        self.repo_owner = None
        self.repo_name = None
        self._init_github()
    
    def _init_github(self):
        """初始化 GitHub 配置"""
        try:
            # 從 Streamlit secrets 獲取配置
            github_config = st.secrets.get("github", {})
            self.github_token = github_config.get("token")
            self.repo_owner = github_config.get("owner")
            self.repo_name = github_config.get("repo")
            
            if self.github_token and self.repo_owner and self.repo_name:
                # 靜默模式，不顯示配置訊息
                pass
            else:
                # 靜默模式，不顯示配置訊息
                pass
        except Exception as e:
            st.error(f"❌ GitHub 配置失敗：{str(e)}")
    
    def is_cloud_mode(self) -> bool:
        """檢查是否為雲端模式"""
        return all([self.github_token, self.repo_owner, self.repo_name])
    
    def upload_file(self, file_path: str, file_name: str) -> Optional[str]:
        """上傳檔案到 GitHub"""
        if not self.is_cloud_mode():
            return None
        
        try:
            # 讀取檔案內容
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # 編碼為 base64
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            # 構建 GitHub API URL
            api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/templates/{file_name}"
            
            # 準備請求數據
            data = {
                "message": f"Upload template: {file_name}",
                "content": encoded_content,
                "branch": "main"
            }
            
            # 發送請求
            import requests
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.put(api_url, json=data, headers=headers)
            
            if response.status_code in [200, 201]:
                st.success(f"✅ 檔案已上傳到 GitHub: {file_name}")
                return f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/main/templates/{file_name}"
            else:
                st.error(f"❌ 上傳失敗: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"❌ 上傳檔案錯誤：{str(e)}")
            return None
    
    def download_file(self, file_name: str) -> Optional[str]:
        """從 GitHub 下載檔案"""
        if not self.is_cloud_mode():
            return None
        
        try:
            # 構建原始檔案 URL
            raw_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/main/templates/{file_name}"
            
            # 下載檔案
            import requests
            response = requests.get(raw_url)
            
            if response.status_code == 200:
                # 保存到臨時檔案
                temp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(temp_dir, file_name)
                
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                
                st.success(f"✅ 檔案已下載: {file_name}")
                return temp_path
            else:
                st.error(f"❌ 下載失敗: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"❌ 下載檔案錯誤：{str(e)}")
            return None
    
    def delete_file(self, file_name: str) -> bool:
        """從 GitHub 刪除檔案"""
        if not self.is_cloud_mode():
            return False
        
        try:
            # 獲取檔案的 SHA
            api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/templates/{file_name}"
            
            import requests
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # 獲取檔案信息
            response = requests.get(api_url, headers=headers)
            if response.status_code != 200:
                st.error(f"❌ 無法獲取檔案信息: {response.status_code}")
                return False
            
            file_info = response.json()
            sha = file_info['sha']
            
            # 刪除檔案
            data = {
                "message": f"Delete template: {file_name}",
                "sha": sha,
                "branch": "main"
            }
            
            response = requests.delete(api_url, json=data, headers=headers)
            
            if response.status_code in [200, 201]:
                st.success(f"✅ 檔案已從 GitHub 刪除: {file_name}")
                return True
            else:
                st.error(f"❌ 刪除失敗: {response.text}")
                return False
                
        except Exception as e:
            st.error(f"❌ 刪除檔案錯誤：{str(e)}")
            return False

# 移除全局實例化，改為在需要時創建實例 