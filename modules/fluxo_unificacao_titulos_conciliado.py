# modules/fluxo_unificacao_titulos_conciliado.py
import streamlit as st
import pandas as pd

def executar():
    if "df_titulos_extraido" not in st.session_state or "df_conciliado_bruto" not in st.session_state:
        st.error("Títulos e conciliação anterior precisam estar extraídos para unificar.")
        return

    df_titulos = st.session_state["df_titulos_extraido"]
    df_conciliado = st.session_state["df_conciliado_bruto"]

    # Confirma se possuem as mesmas colunas
    if not set(df_titulos.columns) == set(df_conciliado.columns):
        st.warning("As colunas dos dois DataFrames não coincidem. A unificação pode gerar campos ausentes.")
        st.write("Colunas títulos:", df_titulos.columns.tolist())
        st.write("Colunas conciliação anterior:", df_conciliado.columns.tolist())

    # Concatena os dois DataFrames
    df_unificado = pd.concat([df_conciliado, df_titulos], ignore_index=True)

    # Armazena no session_state para uso posterior
    st.session_state["df_unificado"] = df_unificado

    st.markdown("### Títulos Unificados (Conciliação Anterior + Títulos Novos)")
    st.dataframe(df_unificado, use_container_width=True)

    st.success("Unificação concluída com sucesso.")
