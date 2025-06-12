# modules/fluxo_conciliacao.py
import streamlit as st
import pandas as pd

def executar():
    st.markdown("#### ⚖️ Relatório Analítico de Conciliação")

    if "df_titulos" not in st.session_state or "df_baixas" not in st.session_state:
        st.warning("Títulos e/ou Baixas ainda não foram carregados.")
        return

    df_titulos = st.session_state["df_titulos"].copy()
    df_baixas = st.session_state["df_baixas"].copy()

    # Renomeia e padroniza campos
    df_titulos_ren = df_titulos.rename(columns={
        "Fornecedor": "FORNECEDOR",
        "Número do Título": "NUMERO DOC",
        "Data de Emissão": "EMISSÃO",
        "Data de Vencimento": "VENCIMENTO",
        "Valor do Título": "VALOR"
    })
    df_titulos_ren["TIPO"] = "Título"
    df_titulos_ren["DATA PAGAMENTO"] = ""

    df_baixas_ren = df_baixas.rename(columns={
        "Fornecedor/Cliente": "FORNECEDOR",
        "Número do Título": "NUMERO DOC",
        "Data de Pagamento": "DATA PAGAMENTO",
        "Valor Pago": "VALOR"
    })
    df_baixas_ren["TIPO"] = "Baixa"
    df_baixas_ren["EMISSÃO"] = ""
    df_baixas_ren["VENCIMENTO"] = ""

    # Normaliza valor
    df_baixas_ren["VALOR"] = df_baixas_ren["VALOR"].replace({',': '.', 'R$': '', '\s': ''}, regex=True).astype(str)
    df_baixas_ren["VALOR"] = "-" + df_baixas_ren["VALOR"]

    df_conciliado = pd.concat([df_titulos_ren, df_baixas_ren], ignore_index=True)
    df_conciliado["NUMERO DOC"] = df_conciliado["NUMERO DOC"].astype(str).str.zfill(9)

    # Converte datas
    for campo in ["EMISSÃO", "VENCIMENTO", "DATA PAGAMENTO"]:
        df_conciliado[campo] = pd.to_datetime(df_conciliado[campo], errors="coerce", dayfirst=True)

    # Ordena
    df_conciliado = df_conciliado.sort_values(by=["NUMERO DOC", "DATA PAGAMENTO", "TIPO"], ascending=[True, True, False])

    st.dataframe(df_conciliado, use_container_width=True)
    st.session_state["df_conciliado"] = df_conciliado
