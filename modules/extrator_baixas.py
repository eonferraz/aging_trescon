# extrator_baixas.py
import streamlit as st
import pandas as pd
import re

# Campos esperados para extração
CAMPOS_BAIXAS = [
    "Fornecedor/Cliente",
    "Número do Título",
    "Data de Pagamento",
    "Valor Pago"
]

# Lista de regexs alternativas para cada campo
REGEX_SUGERIDA_MULTIPLA = {
    "Fornecedor/Cliente": [
        r"(?i)(?:DEV\s+NF\s+\d+\s+CF\s+NF\s+\d+\s+DE\s+)([A-Z0-9\s\.\-/]+)",
        r"(?i)(?:DE\s+)([A-Z0-9\s\.\-/]+?)\s*(?:RECLASS|LANCTO|REF|$)",
        r"(?i)([A-Z0-9\s\.\-/]+?(?:LTDA|S/A|SA|LTD|Ltda|S\.A\.))"
    ],
    "Número do Título": [
        r"(?i)(?:NF[:\- ]*|NFE[:\- ]*|REF\s*NF\s*|CF\s*NF\s*|TIT\s*AB[-\s]*|EXPORT[:\- ]*|SERV[:\- ]*)?(\d{5,})"
    ],
    "Data de Pagamento": [
        r"(?i)(\d{2}/\d{2}/\d{2,4})$"
    ],
    "Valor Pago": [
        r"(?i)VALOR[:\- R$]*([\d\.,]+)"
    ]
}


def aplicar_regex_em_coluna_multiplas(df, coluna, lista_regex):
    base = df[coluna].astype(str)
    resultado_final = pd.Series(["" for _ in range(len(base))], index=base.index)

    for regex in lista_regex:
        extraido = base.str.extract(regex, expand=False)
        if isinstance(extraido, pd.DataFrame):
            extraido = extraido[0]  # se vier DataFrame, pega a primeira coluna
        resultado_final = resultado_final.where(resultado_final != "", extraido)

    return resultado_final


def executar(df):
    if df.empty or df.shape[1] == 0:
        st.warning("Nenhum dado disponível para análise. Importe os dados de baixas primeiro.")
        return

    colunas = df.columns.tolist()
    campos_mapeados = {}
    campos_com_tratamento = {}

    #-------------------------------------------------------------------------------------------------------------------
    st.markdown("#### 🧽 Mapeamento de Campos para Baixas")

    col1, col2, col3, col4 = st.columns(4)

    for i, campo in enumerate(CAMPOS_BAIXAS):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"**{campo}**")
            coluna_selecionada = st.selectbox("", colunas, key=f"sel_col_baixas_{campo}")
            precisa_tratar = st.checkbox("Ajustar?", key=f"chk_regex_baixas_{campo}", value=True)

        campos_mapeados[campo] = coluna_selecionada
        campos_com_tratamento[campo] = precisa_tratar

    st.markdown("---")
    st.markdown("#### ✨ Resultado da Extração de Baixas")

    df_resultado = pd.DataFrame()

    for campo, coluna in campos_mapeados.items():
        coluna_original = df[coluna].fillna("").astype(str).str.strip()

        if campos_com_tratamento[campo]:
            lista_regex = REGEX_SUGERIDA_MULTIPLA.get(campo, [])
            extraido = aplicar_regex_em_coluna_multiplas(df, coluna, lista_regex).fillna("").astype(str).str.strip()
            valores_finais = extraido.combine_first(coluna_original)
        else:
            valores_finais = coluna_original

        if campo == "Número do Título":
            df_resultado[campo] = (
                valores_finais
                .str.replace(".0", "", regex=False)
                .str.zfill(9)
            )
        elif campo == "Valor Pago":
            df_resultado[campo] = (
                valores_finais
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
        else:
            df_resultado[campo] = valores_finais

    st.dataframe(df_resultado, use_container_width=True)
    st.session_state["df_baixas"] = df_resultado
