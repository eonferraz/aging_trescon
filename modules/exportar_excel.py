# modules/exportar_excel.py
import pandas as pd
import io
import streamlit as st

def executar(df: pd.DataFrame):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter", datetime_format="dd/mm/yyyy") as writer:
        df.to_excel(writer, index=False, sheet_name="Conciliação")

    st.download_button(
        label="📥 Baixar Relatório em Excel",
        data=output.getvalue(),
        file_name="relatorio_conciliacao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="botao_download_conciliacao"  # ✅ chave única para evitar duplicidade
    )
