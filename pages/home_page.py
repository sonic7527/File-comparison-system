# 檔名: pages/home_page.py
# 系統首頁

import streamlit as st
from datetime import datetime

def show_home_page():
    """顯示系統首頁"""
    
    # 設備檢測和標題（隱藏式）
    st.markdown("""
    <script>
    // 設備檢測（後台運行）
    (function() {
        const userAgent = navigator.userAgent;
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
        const isTablet = /iPad|Android(?=.*\\bMobile\\b)/i.test(userAgent);
        
        if (isMobile && !isTablet) {
            document.body.classList.add('mobile-device');
        } else if (isTablet) {
            document.body.classList.add('tablet-device');
        } else {
            document.body.classList.add('desktop-device');
        }
    })();
    </script>
    """, unsafe_allow_html=True)
    
    # 系統標題和介紹
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #2E86AB; font-size: 3rem; margin-bottom: 1rem;'>
            📄 歡迎使用北大文件比對與範本管理系統
        </h1>
        <p style='font-size: 1.3rem; color: #666; margin-bottom: 2rem;'>
            智慧化的PDF文件處理解決方案，讓您的文件管理更加高效準確
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 系統功能概覽
    st.markdown("## 🚀 系統功能概覽")
    
    # 功能卡片
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🎨 PDF 變數標記</h3>
            <ul>
                <li>📤 上傳PDF範本文件</li>
                <li>🎯 視覺化標記變數位置</li>
                <li>📊 建立變數資料庫</li>
                <li>🔍 範本管理與預覽</li>
            </ul>
            <p><strong>用途：</strong>建立可重複使用的PDF範本</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>🔍 文件比對檢查</h3>
            <ul>
                <li>📊 上傳待檢查的PDF文件</li>
                <li>🎯 多範本智慧比對</li>
                <li>📄 標記頁面精確檢查</li>
                <li>📋 自動生成缺失清單</li>
            </ul>
            <p><strong>用途：</strong>確保文件符合範本要求</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📝 檔案輸入與生成</h3>
            <ul>
                <li>✏️ 根據範本輸入變數值</li>
                <li>🎯 智慧表單界面</li>
                <li>📁 生成標準化文件</li>
                <li>💾 支援多種輸出格式</li>
            </ul>
            <p><strong>用途：</strong>快速產出符合範本的文件</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>⚙️ 範本管理設定</h3>
            <ul>
                <li>📂 範本群組管理</li>
                <li>🏷️ 分類與標籤系統</li>
                <li>📊 使用統計分析</li>
                <li>🔧 系統參數設定</li>
            </ul>
            <p><strong>用途：</strong>有效組織和管理範本庫</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 使用流程
    st.markdown("## 📋 使用流程")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; color: white; margin: 1rem 0;'>
        <h4 style='color: white; text-align: center; margin-bottom: 1.5rem;'>
            🔄 完整工作流程
        </h4>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div style='text-align: center; flex: 1;'>
                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>1️⃣</div>
                <div><strong>建立範本</strong></div>
                <div style='font-size: 0.9rem; opacity: 0.9;'>上傳PDF並標記變數</div>
            </div>
            <div style='font-size: 1.5rem; color: #FFD700;'>→</div>
            <div style='text-align: center; flex: 1;'>
                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>2️⃣</div>
                <div><strong>輸入資料</strong></div>
                <div style='font-size: 0.9rem; opacity: 0.9;'>填寫變數值生成文件</div>
            </div>
            <div style='font-size: 1.5rem; color: #FFD700;'>→</div>
            <div style='text-align: center; flex: 1;'>
                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>3️⃣</div>
                <div><strong>比對檢查</strong></div>
                <div style='font-size: 0.9rem; opacity: 0.9;'>上傳文件進行比對</div>
            </div>
            <div style='font-size: 1.5rem; color: #FFD700;'>→</div>
            <div style='text-align: center; flex: 1;'>
                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>4️⃣</div>
                <div><strong>獲取報告</strong></div>
                <div style='font-size: 0.9rem; opacity: 0.9;'>下載缺失清單</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 快速開始
    st.markdown("## 🎯 快速開始")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎨 開始標記範本", use_container_width=True, type="primary"):
            st.session_state['page_selection'] = '🎨 PDF 變數標記'
            st.rerun()
    
    with col2:
        if st.button("📝 輸入資料生成", use_container_width=True):
            st.session_state['page_selection'] = '📝 檔案輸入與生成'
            st.rerun()
    
    with col3:
        if st.button("🔍 文件比對檢查", use_container_width=True):
            st.session_state['page_selection'] = '🔍 文件比對檢查'
            st.rerun()
    
    # 簡化的系統狀態
    st.markdown("---")
    st.markdown("## 📊 系統狀態")
    
    # 手機友好的雙欄布局
    col1, col2 = st.columns(2)
    
    with col1:
        # 模擬資料
        template_count = 0
        try:
            from core.pdf_annotation_system import PDFAnnotationSystem
            system = PDFAnnotationSystem()
            templates = system.get_templates_list()
            template_count = len(templates) if templates else 0
        except:
            pass
        st.metric("📄 範本數量", template_count)
    
    with col2:
        st.metric("✅ 系統狀態", "正常運行")
    
    # 簡化的使用提示
    st.markdown("## 💡 使用提示")
    
    st.info("""
    **📱 行動裝置最佳化**
    - 支援手機和平板瀏覽
    - 觸控操作友好設計
    - 自動儲存工作進度
    """)
    
    # 技術資訊收合
    with st.expander("🔧 技術資訊"):
        st.markdown("""
        **系統版本：** v3.0 (行動優化版)  
        **支援格式：** PDF文件  
        **瀏覽器：** Chrome, Firefox, Safari  
        **架構：** Streamlit + SQLite
        """)

if __name__ == "__main__":
    show_home_page()