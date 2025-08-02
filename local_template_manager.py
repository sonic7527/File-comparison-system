#!/usr/bin/env python3
"""
本地範本管理工具
讓您可以在本地管理範本，然後一鍵同步到雲端
"""

import os
import shutil
import subprocess
import streamlit as st
from pathlib import Path

def copy_template_to_data(source_path, template_type="excel"):
    """將範本文件複製到 data 目錄"""
    data_dir = Path("data")
    
    if template_type == "excel":
        target_dir = data_dir / "excel"
    elif template_type == "template":
        target_dir = data_dir / "templates"
    else:
        target_dir = data_dir / "excel_templates"
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 複製文件
    filename = os.path.basename(source_path)
    target_path = target_dir / filename
    
    shutil.copy2(source_path, target_path)
    return str(target_path)

def git_add_and_commit(file_path, commit_message):
    """將文件添加到 Git 並提交"""
    try:
        # 添加文件
        subprocess.run(["git", "add", file_path], check=True)
        
        # 提交
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # 推送到遠程
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Git 操作失敗: {e}")
        return False

def main():
    st.title("📁 本地範本管理工具")
    st.write("在本地管理範本，然後一鍵同步到雲端")
    
    # 選擇操作
    operation = st.selectbox(
        "選擇操作",
        ["添加新範本", "查看現有範本", "同步到雲端"]
    )
    
    if operation == "添加新範本":
        st.header("添加新範本")
        
        # 範本類型
        template_type = st.selectbox(
            "範本類型",
            ["excel", "template", "excel_templates"]
        )
        
        # 文件上傳
        uploaded_file = st.file_uploader(
            "選擇範本文件",
            type=['xlsx', 'xls', 'docx', 'doc'],
            help="支援 Excel 和 Word 文件"
        )
        
        if uploaded_file and st.button("添加範本"):
            # 保存到臨時目錄
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 複製到 data 目錄
            target_path = copy_template_to_data(temp_path, template_type)
            
            # 清理臨時文件
            os.remove(temp_path)
            
            st.success(f"範本已添加到: {target_path}")
            
            # 自動同步到雲端
            if st.button("立即同步到雲端"):
                if git_add_and_commit(target_path, f"Add template: {uploaded_file.name}"):
                    st.success("✅ 範本已同步到雲端！")
                    st.info("Streamlit Cloud 將在幾分鐘內自動重新部署")
                else:
                    st.error("❌ 同步失敗，請檢查 Git 設置")
    
    elif operation == "查看現有範本":
        st.header("現有範本")
        
        data_dir = Path("data")
        if data_dir.exists():
            for subdir in ["excel", "templates", "excel_templates"]:
                subdir_path = data_dir / subdir
                if subdir_path.exists():
                    st.subheader(f"📁 {subdir}")
                    files = list(subdir_path.glob("*"))
                    if files:
                        for file in files:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"📄 {file.name}")
                            with col2:
                                if st.button(f"刪除", key=f"del_{file}"):
                                    file.unlink()
                                    st.success(f"已刪除 {file.name}")
                    else:
                        st.write("無文件")
    
    elif operation == "同步到雲端":
        st.header("同步到雲端")
        
        if st.button("同步所有變更"):
            try:
                # 檢查是否有未提交的變更
                result = subprocess.run(["git", "status", "--porcelain"], 
                                      capture_output=True, text=True)
                
                if result.stdout.strip():
                    st.info("發現未提交的變更，正在同步...")
                    
                    # 添加所有變更
                    subprocess.run(["git", "add", "."], check=True)
                    
                    # 提交
                    subprocess.run(["git", "commit", "-m", "Auto sync: Update templates"], check=True)
                    
                    # 推送
                    subprocess.run(["git", "push", "origin", "main"], check=True)
                    
                    st.success("✅ 所有變更已同步到雲端！")
                    st.info("Streamlit Cloud 將在幾分鐘內自動重新部署")
                else:
                    st.info("沒有新的變更需要同步")
                    
            except subprocess.CalledProcessError as e:
                st.error(f"同步失敗: {e}")
    
    # 顯示當前狀態
    st.header("📊 當前狀態")
    
    # Git 狀態
    try:
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            st.warning("⚠️ 有未提交的變更")
            st.code(result.stdout)
        else:
            st.success("✅ 所有變更已提交")
    except:
        st.error("無法檢查 Git 狀態")

if __name__ == "__main__":
    main() 