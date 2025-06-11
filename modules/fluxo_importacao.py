import streamlit as st
from modules import importar_titulos, extrator_titulos

def executar():
    st.markdown("<div class='custom-subheader'>1.1 Importação do Arquivo</div>", unsafe_allow_html=True)
    importar_titulos.executar()

    if "df_titulos" in st.session_state:
        df = st.session_state["df_titulos"]
        st.markdown("<div class='custom-subheader'>Extração e Mapeamento de Campos</div>", unsafe_allow_html=True)
        extrator_titulos.executar(df)
