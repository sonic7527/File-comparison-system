import streamlit as st

def apply_custom_css():
    """套用自定義CSS樣式"""
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton > button {
            border-radius: 10px;
            padding: 0.5rem 1rem;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab-list"] button {
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background: #4CAF50;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)