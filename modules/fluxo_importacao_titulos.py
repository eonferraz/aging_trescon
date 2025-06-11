import streamlit as st
import pandas as pd

def executar():
    """
    Módulo responsável apenas pela importação do arquivo Excel e seleção da aba.
    O resultado (DataFrame) é salvo no st.session_state['df_titulos'] para uso posterior.
    """

    # Upload do arquivo
    arquivo = st.file_uploader("Selecionar arquivo Excel (.xlsx)", type=["xlsx"])

    if arquivo:
        try:
            # Lista de abas
            abas = pd.ExcelFile(arquivo).sheet_names

            # Escolha da aba
            aba_selecionada = st.selectbox("Selecione a aba a ser importada", abas)

            if aba_selecionada:
                df = pd.read_excel(arquivo, sheet_name=aba_selecionada)
                st.session_state["df_titulos"] = df  # Guarda no estado

                st.success(f"Aba '{aba_selecionada}' carregada com sucesso!")

                # Visualização opcional dos dados
                #with st.expander("📋 Visualizar dados importados"):
                #    st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
