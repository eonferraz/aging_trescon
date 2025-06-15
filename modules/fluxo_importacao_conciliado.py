import streamlit as st
import pandas as pd

def executar():
    arquivo = st.file_uploader("Selecionar arquivo Excel de baixas (.xlsx)", type=["xlsx"])
    if arquivo:
        abas = pd.ExcelFile(arquivo).sheet_names
        aba_selecionada = st.selectbox("Selecione a aba a ser importada", abas)

        if aba_selecionada:
            df = pd.read_excel(arquivo, sheet_name=aba_selecionada)
            st.session_state["df_conciliado_bruto"] = df  # <- ESSENCIAL
            st.success(f"Aba '{aba_selecionada}' carregada com sucesso!")
