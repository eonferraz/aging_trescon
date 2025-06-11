import streamlit as st

def aplicar_css():
    st.markdown("""
        <style>
            /* Fonte base do app */
            body {
                font-size: 10px !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            /* Campos de entrada (inputs e selects) */
            .stTextInput, .stSelectbox, .stSlider, .stFileUploader {
                font-size: 10px !important;
                margin-bottom: 0.3rem !important;
            }

            /* Selectbox especificamente */
            .stSelectbox > div {
                font-size: 10px !important;
            }

            /* File uploader (drag and drop) */
            .stFileUploader {
                font-size: 10px !important;
                line-height: 1.1 !important;
                padding: 6px !important;
            }

            /* Tabelas (dataframe) */
            .stDataFrame {
                border-radius: 6px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                font-size: 10px !important;
                line-height: 1.2 !important;
            }

            /* Tabela interna */
            .stDataFrame table {
                font-size: 10px !important;
                line-height: 1.1 !important;
            }

            /* Expander (visualização de dados) */
            .stExpander .streamlit-expanderHeader {
                font-weight: bold;
                background-color: #f5f5f5;
                border-radius: 6px;
                font-size: 10px !important;
                padding: 4px 8px !important;
            }

            /* Botões */
            .stButton>button {
                font-size: 10px !important;
                padding: 4px 10px !important;
                transition: all 0.3s ease;
                border-radius: 5px;
            }

            .stButton>button:hover {
                transform: translateY(-1px);
                box-shadow: 0 3px 6px rgba(0,0,0,0.1);
            }

            /* Mensagens (info, success, error) */
            .stAlert {
                font-size: 10px !important;
                padding: 8px 10px !important;
                line-height: 1.3 !important;
                border-radius: 6px !important;
                margin-bottom: 0.5rem !important;
            }

            /* Cabeçalho do app */
            .header {
                background-color: white;
                padding: 12px;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
        </style>
    """, unsafe_allow_html=True)
