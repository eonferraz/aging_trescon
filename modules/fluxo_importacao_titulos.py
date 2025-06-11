import streamlit as st
from modules import importar_titulos, extrator_titulos

def executar():
    """
    Orquestra a sequência de importação e extração assistida de campos.
    """

    # Inicializa a etapa, se ainda não existir
    if "etapa" not in st.session_state:
        st.session_state["etapa"] = "importacao"

    # Etapa 1: Importação e extração assistida
    if st.session_state.get("etapa") == "importacao":
        importar_titulos.executar()

        if "df_titulos" in st.session_state:
            df = st.session_state["df_titulos"]
            extrator_titulos.executar(df)

    # Etapa futura: conteúdo oculto após o botão "Próximo"
    elif st.session_state.get("etapa") == "proxima_etapa":
        st.success("✅ Etapa de importação e extração concluída. Pronto para a próxima fase.")
