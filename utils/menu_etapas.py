import streamlit as st

# Etapas do processo e seus respectivos rótulos
ETAPAS_MENU = {
    "importacao_titulos": "📥 Importação de Títulos",
    "extracao_titulos": "🧠 Extração de Títulos",
    "importacao_baixas": "📥 Importação de Baixas",
    "extracao_baixas": "🧠 Extração de Baixas",
    "conciliacao": "🔄 Conciliação",
    "exportacao": "📤 Exportação"
}

def exibir_menu_lateral():
    """
    Renderiza o menu lateral com as etapas do processo e atualiza o estado da etapa selecionada.
    """
    if "etapa" not in st.session_state:
        st.session_state["etapa"] = "importacao_titulos"

    etapa_selecionada = st.sidebar.radio(
        "🔽 Navegar entre etapas",
        options=list(ETAPAS_MENU.keys()),
        format_func=lambda etapa: ETAPAS_MENU[etapa],
        index=list(ETAPAS_MENU.keys()).index(st.session_state["etapa"])
    )

    st.session_state["etapa"] = etapa_selecionada
