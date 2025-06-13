#Esse fluxo faz a importação do relatório consolidado

import streamlit as st
import pandas as pd

def executar():
    """
    Módulo responsável apenas pela importação do arquivo Excel e seleção da aba.
    O resultado (DataFrame) é salvo no st.session_state['df_consolidado'] para uso posterior.
    """

    # Upload do arquivo
    arquivo = st.file_uploader("Selecionar arquivo Excel (.xlsx)", type=["xlsx"])

    if arquivo:
        try:
            # Lista de abas
            abas = pd.ExcelFile(arquivo).sheet_names

            # Criação das colunas lado a lado
            col1, col2 = st.columns([2, 3])  # ajuste a proporção conforme necessário

            with col1:
                aba_selecionada = st.selectbox("Selecione a aba a ser importada", abas)

            with col2:
                if aba_selecionada:
                    st.success(f"Aba '{aba_selecionada}' carregada com sucesso!")

            if aba_selecionada:
                df = pd.read_excel(arquivo, sheet_name=aba_selecionada)
                st.session_state["df_consolidado"] = df  # Guarda no estado

        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
