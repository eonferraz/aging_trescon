import streamlit as st

def aplicar_css():
    st.markdown("""
        <style>
            body {
                font-size: 14px !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .stTextInput, .stSelectbox, .stSlider, .stFileUploader {
                margin-bottom: 0.5rem;
            }
            .stDataFrame {
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            }
            .stButton>button {
                transition: all 0.3s ease;
                border-radius: 6px;
            }
            .stButton>button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .stExpander .streamlit-expanderHeader {
                font-weight: bold;
                background-color: #f8f9fa;
                border-radius: 8px 8px 0 0;
            }
            .stAlert {
                border-radius: 8px;
            }
            .header {
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
        </style>
    """, unsafe_allow_html=True)
