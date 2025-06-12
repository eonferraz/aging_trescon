# modules/fluxo_exportacao.py
import streamlit as st
from modules.exportar_excel import executar as exportar_excel

def executar():
    st.markdown("#### 📤 Exportação do Relatório de Conciliação")

    if "df_conciliado" not in st.session_state:
        st.warning("O relatório de conciliação ainda não foi gerado.")
        return

    df = st.session_state["df_conciliado"]
    exportar_excel(df)
