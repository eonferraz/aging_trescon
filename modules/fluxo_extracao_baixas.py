import streamlit as st
from modules import extrator_baixas

def executar():
    """
    Fluxo da etapa: Extração assistida dos dados de baixas financeiras.
    """
    if "df_baixas" not in st.session_state:
        st.warning("Os dados das baixas ainda não foram importados.")
        return

    df = st.session_state["df_baixas"]
    extrator_baixas.executar(df)
