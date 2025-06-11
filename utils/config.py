import streamlit as st

VERSAO_APP = "1.1"
EMPRESA = "Trescon"

def configurar_pagina():
    st.set_page_config(
        page_title="Relatório de Aging - Conciliador",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )  
