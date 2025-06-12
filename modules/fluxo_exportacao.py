# modules/fluxo_exportacao.py

import streamlit as st
import pandas as pd
import io

def executar():
    st.markdown("### 📦 Exportação dos Dados Conciliados")

    if "df_titulos" not in st.session_state or "df_baixas" not in st.session_state:
        st.warning("Títulos e/ou Baixas ainda não estão carregados.")
        return

    # Placeholder até termos a conciliação final consolidada
    df_resultado = pd.concat([
        st.session_state["df_titulos"].assign(Origem="Títulos"),
        st.session_state["df_baixas"].assign(Origem="Baixas")
    ])

    st.dataframe(df_resultado, use_container_width=True)

    # Exportação como Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_resultado.to_excel(writer, index=False, sheet_name="Resultado")
        writer.save()

    st.download_button(
        label="🔳 Baixar Arquivo Excel",
        data=buffer.getvalue(),
        file_name="resultado_conciliado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success("Arquivo pronto para download.")
