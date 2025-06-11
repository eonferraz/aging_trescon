import streamlit as st
import pandas as pd
import io
import re
import difflib
import logging
from datetime import datetime

# Configurações iniciais
st.set_page_config(page_title="Aging - Conciliador", layout="wide", page_icon="📊")

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes
DEFAULT_CUTOFF = 0.4
MAX_UPLOAD_SIZE = 200  # MB

# CSS customizado
st.markdown("""
    <style>
        /* Melhorias gerais */
        body {
            font-size: 14px !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Melhorar inputs */
        .stTextInput, .stSelectbox, .stSlider, .stFileUploader {
            margin-bottom: 0.5rem;
        }
        
        /* Melhorar tabelas */
        .stDataFrame {
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        
        /* Botões */
        .stButton>button {
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
        }
        
        /* Mensagens de erro */
        .stAlert {
            border-radius: 8px;
        }
        
        /* Cabeçalho */
        .header {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)
