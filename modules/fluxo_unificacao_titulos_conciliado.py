# modules/fluxo_unificacao_titulos_conciliado.py
import streamlit as st
import pandas as pd

def executar():
    # Confirma se os dois DataFrames existem no session_state
    if "df_titulos_extraido" not in st.session_state:
        st.warning("Os títulos ainda não foram extraídos.")
        return

    if "df_conciliado_bruto" not in st.session_state:
        st.warning("A conciliação anterior ainda não foi extraída.")
        return

    df_titulos = st.session_state["df_titulos_extraido"]
    df_conciliado = st.session_state["df_conciliado_bruto"]

    # Verificação de consistência de colunas
    if not set(df_titulos.columns) == set(df_conciliado.columns):
        st.warning("As colunas dos dois DataFrames não coincidem. A unificação pode gerar campos ausentes.")
        st.write("Colunas títulos:", df_titulos.columns.tolist())
        st.write("Colunas conciliação anterior:", df_conciliado.columns.tolist())

    # Realiza a unificação
    df_unificado = pd.concat([df_conciliado, df_titulos], ignore_index=True)

    st.session_state["df_unificado"] = df_unificado

    st.markdown("### Resultado da Unificação (Conciliação Anterior + Títulos Novos)")
    st.dataframe(df_unificado, use_container_width=True)

    st.success("Unificação realizada com sucesso!")
