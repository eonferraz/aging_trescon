# modules/fluxo_conciliacao.py

import streamlit as st

def executar():
    st.markdown("### 🔄 Conciliação entre Títulos e Baixas")
    
    if "df_titulos" not in st.session_state or "df_baixas" not in st.session_state:
        st.warning("Títulos e/ou Baixas ainda não foram carregados.")
        return

    df_titulos = st.session_state["df_titulos"]
    df_baixas = st.session_state["df_baixas"]

    # Aqui virá a lógica real de conciliação
    st.info("🔧 Módulo de conciliação ainda em desenvolvimento...")

    # Para fins de teste:
    st.write("Títulos disponíveis:", df_titulos.shape)
    st.write("Baixas disponíveis:", df_baixas.shape)

    # Seta um estado para permitir exportação depois
    st.session_state["conciliacao_finalizada"] = True
