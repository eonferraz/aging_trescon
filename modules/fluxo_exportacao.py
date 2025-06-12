# utils/exportar_excel.py
import pandas as pd
import io
import streamlit as st

def exportar_relatorio_conciliacao(df: pd.DataFrame):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Conciliação")
        writer.close()
    st.download_button(
        label="📥 Baixar Relatório em Excel",
        data=output.getvalue(),
        file_name="relatorio_conciliacao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
