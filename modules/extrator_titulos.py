import streamlit as st
import pandas as pd
import re

# Campos lógicos a extrair/tratar
CAMPOS_LOGICOS = [
    "Fornecedor",
    "Número do Título",
    "Data de Emissão",
    "Data de Vencimento",
    "Valor do Título"
]

# Expressões regulares sugeridas por campo
REGEX_SUGERIDA = {
    "Fornecedor": r"(?i)CLIENTE\s*[:\-]?\s*(.+)",
    "Número do Título": r"(?i)(?:NF(?:E)?[:\- ]*)(\d{6,})",
    "Data de Emissão": r"(?i)EMISS(?:AO|ÃO)?[:\- ]+(\d{2}/\d{2}/\d{4})",
    "Data de Vencimento": r"(?i)VENC(?:TO|IMENTO)?[:\- ]+(\d{2}/\d{2}/\d{4})",
    "Valor do Título": r"(?i)VALOR[:\- R$]*([\d\.,]+)"
}

# Aplica uma expressão regular (regex) à coluna do DataFrame e retorna os dados extraídos.
def aplicar_regex_em_coluna(df, coluna, regex):
    try:
        return df[coluna].astype(str).str.extract(regex, expand=False)
    except Exception as e:
        st.error(f"Erro ao aplicar regex na coluna '{coluna}': {e}")
        return None

# Função principal de execução
def executar(df):
    if st.session_state.get("etapa") == "proxima_etapa":
        return

    if df.empty or df.shape[1] == 0:
        st.warning("Nenhum dado disponível para análise. Importe os títulos primeiro.")
        return

    colunas = df.columns.tolist()
    campos_mapeados = {}
    campos_com_tratamento = {}

    col_esq, col_dir = st.columns([3, 2])

    with col_esq:
        st.markdown("<div class='custom-subheader'>Visuaização dos Dados Importados</div>", unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)

    with col_dir:
        st.markdown("<div class='custom-subheader'>Mapeamento dos Campos</div>", unsafe_allow_html=True)
        for i, campo in enumerate(CAMPOS_LOGICOS):
            campos, sel_col, chk = st.columns([2, 2, 1])

            with campos:
                st.markdown(f"`{campo}`")

            with sel_col:
                coluna_selecionada = st.selectbox(
                    "",
                    colunas,
                    key=f"sel_col_{i}"
                )

            with chk:
                precisa_tratar = st.checkbox("Regex?", key=f"chk_regex_{i}", value=True)

            campos_mapeados[campo] = coluna_selecionada
            campos_com_tratamento[campo] = precisa_tratar

    st.markdown("---")
    df_resultado = pd.DataFrame()

    for campo, coluna in campos_mapeados.items():
        if campos_com_tratamento[campo]:
            regex = REGEX_SUGERIDA.get(campo, "")
            extraido = aplicar_regex_em_coluna(df, coluna, regex)

            if campo == "Número do Título":
                df_resultado[campo] = (
                    extraido.fillna("")
                    .astype(str)
                    .str.replace(".0", "", regex=False)
                    .str.strip()
                    .str.zfill(9)
                )
            else:
                df_resultado[campo] = extraido.fillna("")
        else:
            if campo == "Número do Título":
                df_resultado[campo] = (
                    df[coluna].fillna("")
                    .astype(str)
                    .str.replace(".0", "", regex=False)
                    .str.strip()
                    .str.zfill(9)
                )
            else:
                df_resultado[campo] = df[coluna].fillna("")

    st.markdown("### Dados extraídos (tratados)")
    st.dataframe(df_resultado, use_container_width=True)

    st.session_state["df_titulos"] = df_resultado

    st.success("Extração concluída com sucesso.")

    if st.button("\u27a1\ufe0f Próximo"):
        st.session_state["etapa"] = "proxima_etapa"
        st.experimental_rerun()

    st.markdown("---")
