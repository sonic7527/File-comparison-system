import streamlit as st

st.set_page_config(
    page_title="測試側邊欄",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("測試側邊欄功能")

# 側邊欄內容
st.sidebar.markdown("## 🛠️ 功能選單")

function_choice = st.sidebar.selectbox(
    "選擇功能",
    [
        "🏠 系統首頁",
        "🎨 PDF 變數標記",
        "📝 檔案輸入與生成", 
        "🔍 文件比對檢查", 
        "⚙️ 範本管理設定",
        "📄 智能文件生成"
    ]
)

st.write(f"您選擇了：{function_choice}")

if function_choice == "📄 智能文件生成":
    st.success("✅ 智能文件生成功能已選擇！") 