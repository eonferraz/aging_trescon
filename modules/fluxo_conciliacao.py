# modules/fluxo_conciliacao.py
import streamlit as st
import pandas as pd
import io
from unidecode import unidecode
from rapidfuzz import fuzz, process

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

def normalizar_fornecedor(nome):
    nome = unidecode(str(nome)).upper()
    nome = nome.replace(" LTDA", "").replace(" LTDA.", "").replace(" LTD", "").replace(" LTD.", "")
    nome = nome.replace(" S/A", "").replace(" S. A.", "")
    nome = nome.replace("AUTOMOVEIS", "").replace("AUTOM", "")
    nome = nome.replace(" COM E PARTIC", "")
    nome = nome.replace(" - ARMAZEM AILN", "")
    nome = nome.strip()
    return nome

def mapear_fuzzy(lista_nomes, threshold=85):
    nomes_base = []
    grupos = {}
    for nome in lista_nomes:
        nome_base = normalizar_fornecedor(nome)
        melhor, score = process.extractOne(nome_base, nomes_base, scorer=fuzz.token_sort_ratio)

        
        resultado = process.extractOne(nome_base, nomes_base, scorer=fuzz.token_sort_ratio)
        if resultado is not None:
            melhor, score = resultado
            if score >= threshold:
                grupos[nome] = melhor
            else:
                nomes_base.append(nome_base)
                grupos[nome] = nome_base
        else:
            nomes_base.append(nome_base)
            grupos[nome] = nome_base
        # if score and score >= threshold:
        #     grupos[nome] = melhor
        # else:
        #     nomes_base.append(nome_base)
        #     grupos[nome] = nome_base
    return grupos

def executar():
    st.markdown("#### ⚖️ Relatório Analítico de Conciliação")

    if "df_titulos" not in st.session_state or "df_baixas" not in st.session_state:
        st.warning("Títulos e/ou Baixas ainda não foram carregados.")
        return

    df_titulos = st.session_state["df_titulos"].copy()
    df_baixas = st.session_state["df_baixas"].copy()

    # Padroniza campos dos títulos
    titulos = df_titulos.rename(columns={
        "Fornecedor": "FORNECEDOR TITULO",
        "Número do Título": "NUMERO DOC TITULO",
        "Data de Emissão": "EMISSAO",
        "Data de Vencimento": "VENCIMENTO",
        "Valor do Título": "VALOR NOMINAL"
    })
    titulos["TIPO"] = "Título"
    titulos["DATA PAGAMENTO"] = pd.NaT
    titulos["NUMERO DOC BAIXA"] = None
    titulos["FORNECEDOR BAIXA"] = None
    titulos["VALOR NOMINAL"] = (
        titulos["VALOR NOMINAL"].astype(str).replace({',': '.', 'R\$': '', '\s': ''}, regex=True)
    )
    titulos["VALOR NOMINAL"] = pd.to_numeric(titulos["VALOR NOMINAL"], errors="coerce").fillna(0)

    # Padroniza campos das baixas
    baixas = df_baixas.rename(columns={
        "Fornecedor/Cliente": "FORNECEDOR BAIXA",
        "Número do Título": "NUMERO DOC BAIXA",
        "Data de Pagamento": "DATA PAGAMENTO",
        "Valor Pago": "VALOR NOMINAL"
    })
    baixas["TIPO"] = "Baixa"
    baixas["EMISSAO"] = pd.NaT
    baixas["VENCIMENTO"] = pd.NaT
    baixas["NUMERO DOC TITULO"] = None
    baixas["FORNECEDOR TITULO"] = None
    baixas["VALOR NOMINAL"] = (
        baixas["VALOR NOMINAL"].astype(str).replace({',': '.', 'R\$': '', '\s': ''}, regex=True)
    )
    baixas["VALOR NOMINAL"] = pd.to_numeric(baixas["VALOR NOMINAL"], errors="coerce").fillna(0) * -1

    # Concatena e normaliza documentos
    df = pd.concat([titulos, baixas], ignore_index=True)
    df["NUMERO DOC TITULO"] = df["NUMERO DOC TITULO"].fillna(df["NUMERO DOC BAIXA"])
    df["NUMERO DOC BAIXA"] = df["NUMERO DOC BAIXA"].fillna(df["NUMERO DOC TITULO"])
    df["NUMERO DOC"] = df["NUMERO DOC TITULO"].fillna(df["NUMERO DOC BAIXA"])
    df["NUMERO DOC"] = df["NUMERO DOC"].astype(str).str.zfill(9)

    for campo in ["EMISSAO", "VENCIMENTO", "DATA PAGAMENTO"]:
        df[campo] = pd.to_datetime(df[campo], errors="coerce", dayfirst=True)

    df["FORNECEDOR TITULO"] = df["FORNECEDOR TITULO"].fillna("")
    df["FORNECEDOR BAIXA"] = df["FORNECEDOR BAIXA"].fillna("")

    df["FORNECEDOR CONSIDERADO"] = df["FORNECEDOR TITULO"]
    df.loc[df["TIPO"] == "Baixa", "FORNECEDOR CONSIDERADO"] = df["FORNECEDOR BAIXA"]

    # Aplica agrupamento inteligente
    mapa_fuzzy = mapear_fuzzy(df["FORNECEDOR CONSIDERADO"].unique())
    df["FORNECEDOR AJUSTADO"] = df["FORNECEDOR CONSIDERADO"].map(mapa_fuzzy)

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

    df = df[[
        "TIPO", "FORNECEDOR TITULO", "FORNECEDOR BAIXA", "FORNECEDOR CONSIDERADO", "FORNECEDOR AJUSTADO",
        "NUMERO DOC TITULO", "NUMERO DOC BAIXA", "NUMERO DOC",
        "EMISSAO", "VENCIMENTO", "DATA PAGAMENTO",
        "VALOR NOMINAL", "STATUS DA CONCILIAÇÃO"
    ]]

    df = df.sort_values(by=["NUMERO DOC", "TIPO", "DATA PAGAMENTO"], ascending=[True, False, True])

    st.dataframe(df, use_container_width=True)
    st.session_state["df_conciliado"] = df

    # Exportação
    exportar_excel(df)
