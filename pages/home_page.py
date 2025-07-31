# 檔名: pages/home_page.py
# 系統首頁 - 已針對手機版優化

import streamlit as st

def show_home_page():
    """顯示系統首頁，包含桌面和手機兩種佈局"""
    
    # --- 統一的系統標題和介紹 ---
    st.markdown("""
    <div style='text-align: center; padding: 2rem 1rem;'>
        <h1 style='color: #2E86AB; margin-bottom: 1rem;'>
            📄 北大文件比對與範本管理系統
        </h1>
        <p style='font-size: 1.2rem; color: #555;'>
            一個智慧化的文件處理解決方案
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # --- 桌面版佈局 (Desktop-only) ---
    st.markdown('<div class="desktop-only">', unsafe_allow_html=True)
    st.markdown("## 🚀 系統功能概覽")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🎨 PDF 變數標記</h3>
            <ul>
                <li>上傳PDF範本文件</li>
                <li>視覺化標記變數位置</li>
                <li>建立可重複使用的範本</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="feature-card">
            <h3>🔍 文件比對檢查</h3>
            <ul>
                <li>上傳待檢查的PDF文件</li>
                <li>多範本智慧比對</li>
                <li>自動生成缺失清單</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📝 檔案輸入與生成</h3>
            <ul>
                <li>根據範本輸入變數值</li>
                <li>生成標準化文件</li>
                <li>支援多種輸出格式</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="feature-card">
            <h3>⚙️ 範本管理設定</h3>
            <ul>
                <li>範本群組管理</li>
                <li>分類與標籤系統</li>
                <li>有效組織和管理範本庫</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


    # --- 手機版佈局 (Mobile-only) ---
    st.markdown('<div class="mobile-only">', unsafe_allow_html=True)
    st.markdown("## 🚀 功能列表")
    st.markdown("""
        <div class='mobile-feature-list'>
            <div class="feature-card"><h3>🎨 PDF 變數標記</h3></div>
            <div class="feature-card"><h3>📝 檔案輸入與生成</h3></div>
            <div class="feature-card"><h3>🔍 文件比對檢查</h3></div>
            <div class="feature-card"><h3>⚙️ 範本管理設定</h3></div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    
    # --- 統一的工作流程 ---
    st.markdown("## 📋 完整工作流程")
    st.markdown("""
    <div class='workflow-container' style='display: flex; justify-content: space-around; align-items: center; 
                 background: #f0f2f6; padding: 2rem; border-radius: 15px; margin: 1rem 0;'>
        <div class='workflow-step' style='text-align: center; flex: 1;'>
            <div style='font-size: 2rem;'>1️⃣</div><div><strong>建立範本</strong></div>
        </div>
        <div class='workflow-arrow' style='font-size: 1.5rem; color: #2E86AB;'>→</div>
        <div class='workflow-step' style='text-align: center; flex: 1;'>
            <div style='font-size: 2rem;'>2️⃣</div><div><strong>生成文件</strong></div>
        </div>
        <div class='workflow-arrow' style='font-size: 1.5rem; color: #2E86AB;'>→</div>
        <div class='workflow-step' style='text-align: center; flex: 1;'>
            <div style='font-size: 2rem;'>3️⃣</div><div><strong>比對檢查</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- 統一的系統狀態 ---
    st.markdown("## 📊 系統狀態")
    try:
        from core.pdf_annotation_system import PDFAnnotationSystem
        system = PDFAnnotationSystem()
        templates = system.get_templates_list()
        template_count = len(templates) if templates else 0
    except Exception:
        template_count = "N/A"
        
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📄 範本總數", template_count)
    with col2:
        st.metric("✅ 系統狀態", "運行中")

if __name__ == "__main__":
    # 為了能獨立測試此頁面，我們也加上CSS的引用
    st.set_page_config(layout="wide")
    try:
        from utils.ui_components import apply_custom_css
        apply_custom_css()
    except ImportError:
        st.warning("Could not import custom CSS.")
    show_home_page()
