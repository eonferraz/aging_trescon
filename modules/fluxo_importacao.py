import streamlit as st
from modules import importar_titulos, extrator_titulos

def executar():
    """
    Orquestra a sequência de importação e extração assistida de campos.
    """
    # Passo 1: Importar planilha
    #st.markdown("<div class='custom-subheader'>1️⃣ Importação dos Títulos Financeiros</div>", unsafe_allow_html=True)
    importar_titulos.executar()

    # Passo 2: Se dados foram carregados, iniciar extração assistida
    if "df_titulos" in st.session_state:
        df = st.session_state["df_titulos"]
        #st.markdown("<div class='custom-subheader'>2️⃣ Extração e Mapeamento de Campos</div>", unsafe_allow_html=True)
        extrator_titulos.executar(df)
