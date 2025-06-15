# modules/fluxo_exportacao.py
import streamlit as st
from modules.fluxo_conciliacao import exportar_excel

def executar():
    if "df_conciliado" not in st.session_state:
        st.warning("⚠️ Nenhum dado conciliado encontrado para exportação.")
        return

    df = st.session_state["df_conciliado"]
    st.markdown("### 📤 Exportação da Conciliação")
    exportar_excel(df)
