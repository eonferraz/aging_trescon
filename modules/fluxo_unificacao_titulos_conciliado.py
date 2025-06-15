# modules/fluxo_unificacao_titulos_conciliado.py
import streamlit as st
import pandas as pd

def executar():
    st.markdown("#### 🔀 Unificação: Títulos + Conciliação Anterior")

    if "df_titulos" not in st.session_state or "df_conciliado_anterior" not in st.session_state:
        st.warning("É necessário extrair tanto os títulos quanto a conciliação anterior antes de unificar.")
        return

    df_titulos = st.session_state["df_titulos"].copy()
    df_conc_anteriores = st.session_state["df_conciliado_anterior"].copy()

    df_unificado = pd.concat([df_titulos, df_conc_anteriores], ignore_index=True)
    st.session_state["df_titulos"] = df_unificado

    st.success("Unificação realizada com sucesso! Os dados estão prontos para seguir para as baixas.")
    st.dataframe(df_unificado, use_container_width=True)
