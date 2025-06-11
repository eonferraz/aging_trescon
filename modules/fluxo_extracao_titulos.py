import streamlit as st
from modules import extrator_titulos

def executar():
    """
    Controla o fluxo da etapa de extração de títulos.
    """
    if "df_titulos" not in st.session_state:
        st.warning("Importe os dados dos títulos antes de prosseguir.")
        return

    df = st.session_state["df_titulos"]
    extrator_titulos.executar(df)
