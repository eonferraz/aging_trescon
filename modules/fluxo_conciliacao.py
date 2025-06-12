# modules/fluxo_conciliacao.py
import streamlit as st
import io
import pandas as pd

def exportar_excel(df: pd.DataFrame):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter", datetime_format="dd/mm/yyyy") as writer:
        df.to_excel(writer, index=False, sheet_name="Conciliação")
    st.download_button(
        label="📥 Baixar Relatório em Excel",
        data=output.getvalue(),
        file_name="relatorio_conciliacao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_conciliacao"
    )

def executar():
    st.markdown("#### ⚖️ Relatório Analítico de Conciliação")

    if "df_titulos" not in st.session_state or "df_baixas" not in st.session_state:
        st.warning("Títulos e/ou Baixas ainda não foram carregados.")
        return

    df_titulos = st.session_state["df_titulos"].copy()
    df_baixas = st.session_state["df_baixas"].copy()

    # Padroniza campos dos títulos
    titulos = df_titulos.rename(columns={
        "Fornecedor": "FORNECEDOR",
        "Número do Título": "NUMERO DOC",
        "Data de Emissão": "EMISSAO",
        "Data de Vencimento": "VENCIMENTO",
        "Valor do Título": "VALOR NOMINAL"
    })
    titulos["TIPO"] = "Título"
    titulos["DATA PAGAMENTO"] = pd.NaT
    titulos["VALOR NOMINAL"] = (
        titulos["VALOR NOMINAL"]
        .astype(str)
        .replace({',': '.', 'R\$': '', '\s': ''}, regex=True)
    )
    titulos["VALOR NOMINAL"] = pd.to_numeric(titulos["VALOR NOMINAL"], errors="coerce").fillna(0)

    # Padroniza campos das baixas
    baixas = df_baixas.rename(columns={
        "Fornecedor/Cliente": "FORNECEDOR",
        "Número do Título": "NUMERO DOC",
        "Data de Pagamento": "DATA PAGAMENTO",
        "Valor Pago": "VALOR NOMINAL"
    })
    baixas["TIPO"] = "Baixa"
    baixas["EMISSAO"] = pd.NaT
    baixas["VENCIMENTO"] = pd.NaT
    baixas["VALOR NOMINAL"] = (
        baixas["VALOR NOMINAL"]
        .astype(str)
        .replace({',': '.', 'R\$': '', '\s': ''}, regex=True)
    )
    baixas["VALOR NOMINAL"] = pd.to_numeric(baixas["VALOR NOMINAL"], errors="coerce").fillna(0) * -1

    # Concatena e organiza
    df = pd.concat([titulos, baixas], ignore_index=True)
    df["NUMERO DOC"] = df["NUMERO DOC"].astype(str).str.zfill(9)

    for campo in ["EMISSAO", "VENCIMENTO", "DATA PAGAMENTO"]:
        df[campo] = pd.to_datetime(df[campo], errors="coerce", dayfirst=True)

    # Calcula status por documento
    status_map = {}
    for doc in df["NUMERO DOC"].unique():
        grupo = df[df["NUMERO DOC"] == doc]
        has_titulo = "Título" in grupo["TIPO"].values
        has_baixa = "Baixa" in grupo["TIPO"].values
        if has_titulo and has_baixa:
            status_map[doc] = "OK"
        elif has_titulo:
            status_map[doc] = "Pagamento não encontrado"
        elif has_baixa:
            status_map[doc] = "Título não encontrado"
        else:
            status_map[doc] = "Inconsistente"

    df["STATUS DA CONCILIAÇÃO"] = df["NUMERO DOC"].map(status_map)

    # Ordena para relatório analítico
    df = df[[
        "TIPO", "NUMERO DOC", "FORNECEDOR", "EMISSAO", "VENCIMENTO", "DATA PAGAMENTO",
        "VALOR NOMINAL", "STATUS DA CONCILIAÇÃO"
    ]]
    df = df.sort_values(by=["NUMERO DOC", "TIPO", "DATA PAGAMENTO"], ascending=[True, False, True])

    st.dataframe(df, use_container_width=True)
    st.session_state["df_conciliado"] = df

    # Exportação
    exportar_excel(df)

