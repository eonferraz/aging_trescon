import streamlit as st
import pandas as pd

def executar():
    st.info("Faça o upload do arquivo de títulos (.xlsx)")

    arquivo = st.file_uploader("Selecionar arquivo Excel", type=["xlsx"])

    if arquivo:
        try:
            df = pd.read_excel(arquivo)

            # Armazenar no session_state para outros módulos
            st.session_state["df_titulos"] = df

            st.success("Arquivo carregado com sucesso!")
            with st.expander("📋 Visualizar dados importados"):
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
