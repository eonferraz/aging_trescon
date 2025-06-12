import streamlit as st
import pandas as pd

def executar():
    """
    Módulo responsável pela importação do arquivo de baixas.
    Permite usar o mesmo arquivo dos títulos ou carregar um novo.
    O resultado (DataFrame) é salvo no st.session_state['df_baixas'].
    """

    st.markdown("### 📥 Importação das Baixas")

    # Opção de usar o mesmo arquivo dos títulos
    usar_arquivo_titulos = st.selectbox(
        "Deseja usar o mesmo arquivo enviado para os títulos?",
        ["Sim", "Não"]
    )

    # Se "Não", mostrar novo file_uploader
    if usar_arquivo_titulos == "Não":
        arquivo = st.file_uploader("Selecionar novo arquivo Excel (.xlsx)", type=["xlsx"])
    else:
        arquivo = st.session_state.get("arquivo_titulos")  # reutiliza se estiver salvo
        if not arquivo:
            st.warning("Nenhum arquivo de títulos encontrado. Faça o upload na etapa anterior.")
            return

    if arquivo:
        try:
            # Lista de abas
            abas = pd.ExcelFile(arquivo).sheet_names

            # Escolha da aba
            col1, col2 = st.columns([2, 3])

            with col1:
                aba_selecionada = st.selectbox("Selecione a aba de baixas a ser importada", abas)

            with col2:
                if aba_selecionada:
                    st.success(f"Aba '{aba_selecionada}' carregada com sucesso!")

            if aba_selecionada:
                df = pd.read_excel(arquivo, sheet_name=aba_selecionada)
                st.session_state["df_baixas"] = df

        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
