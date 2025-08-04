import streamlit as st
import os

def test_secrets():
    st.title("🔍 Secrets 測試")
    
    st.subheader("1. 檢查 st.secrets 結構")
    try:
        st.write("st.secrets 內容：")
        st.json(st.secrets)
    except Exception as e:
        st.error(f"無法讀取 st.secrets：{str(e)}")
    
    st.subheader("2. 檢查環境變數")
    st.write("TURSO_URL:", os.environ.get("TURSO_URL", "未設置"))
    st.write("TURSO_TOKEN:", os.environ.get("TURSO_TOKEN", "未設置"))
    
    st.subheader("3. 嘗試獲取 Turso 配置")
    try:
        turso_url = st.secrets.get("turso", {}).get("url")
        turso_token = st.secrets.get("turso", {}).get("token")
        
        if not turso_url:
            turso_url = os.environ.get("TURSO_URL")
        if not turso_token:
            turso_token = os.environ.get("TURSO_TOKEN")
        
        st.write("Turso URL:", turso_url if turso_url else "未找到")
        st.write("Turso Token:", "已設置" if turso_token else "未找到")
        
        if turso_url and turso_token:
            st.success("✅ Turso 配置完整")
        else:
            st.warning("⚠️ Turso 配置不完整")
            
    except Exception as e:
        st.error(f"配置檢查失敗：{str(e)}")

if __name__ == "__main__":
    test_secrets() 