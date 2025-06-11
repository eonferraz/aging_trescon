import streamlit as st

def aplicar_css():
    st.markdown("""
        <style>
            /* Fonte geral do app */
            body {
                font-size: 10px !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            /* Campos de entrada - menor espaçamento */
            .stTextInput, .stSelectbox, .stSlider, .stFileUploader {
                margin-bottom: 0.3rem !important;
            }

            /* Tabelas - menor fonte e linha compacta */
            .stDataFrame {
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                font-size: 10px !important;
                line-height: 1.0 !important;
            }

            /* Botões */
            .stButton>button {
                font-size: 10px !important;
                padding: 4px 10px !important;
                transition: all 0.3s ease;
                border-radius: 6px;
            }

            .stButton>button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }

            /* Expanders */
            .stExpander .streamlit-expanderHeader {
                font-weight: bold;
                background-color: #f8f9fa;
                border-radius: 8px 8px 0 0;
                font-size: 11px !important;
                padding: 6px !important;
            }

            /* Alertas */
            .stAlert {
                border-radius: 3px;
                font-size: 80px !important;
                padding: 8px 12px !important;
                line-height: 1.3 !important;
                margin-bottom: 0.5rem !important
            }

            /* Cabeçalho principal */
            .header {
                background-color: white;
                padding: 12px;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                margin-bottom: 15px;
            }
        </style>
    """, unsafe_allow_html=True)
