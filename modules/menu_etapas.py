import streamlit as st

# Define as etapas disponíveis e seus rótulos amigáveis
ETAPAS_MENU = {
    "importacao": "📥 Importação",
    "extracao": "🧠 Extração",
    "conciliacao": "🔄 Conciliação",
    "exportacao": "📤 Exportação"
}

def exibir_menu_lateral():
    """
    Renderiza o menu lateral com as etapas e atualiza o estado global da etapa selecionada.
    """
    # Garante etapa inicial
    if "etapa" not in st.session_state:
        st.session_state["etapa"] = "importacao"

    etapa_selecionada = st.sidebar.radio(
        "Navegar entre etapas",
        options=list(ETAPAS_MENU.keys()),
        format_func=lambda etapa: ETAPAS_MENU[etapa],
        index=list(ETAPAS_MENU.keys()).index(st.session_state["etapa"])
    )

    st.session_state["etapa"] = etapa_selecionada
