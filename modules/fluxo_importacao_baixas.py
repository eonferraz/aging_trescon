import streamlit as st
import pandas as pd

def executar():
    """
    Fluxo da etapa: Importação das Baixas Financeiras.
    """
    st.markdown("<div class='custom-subheader'>📥 Importação das Baixas Financeiras</div>", unsafe_allow_html=True)

    # Upload do arquivo Excel
    arquivo = st.file_uploader("Selecionar arquivo Excel de baixas (.xlsx)", type=["xlsx"], key="upload_baixas")

    if arquivo:
        try:
            abas = pd.ExcelFile(arquivo).sheet_names

            col1, col2 = st.columns([2, 3])  # proporção ajustável conforme o espaço

            with col1:
                aba_selecionada = st.selectbox("Selecione a aba de baixas", abas, key="aba_baixas")

            with col2:
                if aba_selecionada:
                    st.success(f"Aba '{aba_selecionada}' carregada com sucesso!")

            if aba_selecionada:
                df = pd.read_excel(arquivo, sheet_name=aba_selecionada)
                st.session_state["df_baixas"] = df
                
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
