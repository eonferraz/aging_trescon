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

REGEX_SUGERIDA = {
    "Fornecedor": r"(?i)(?:CLIENTE[:\-]?\s*|DE\s+|NF\s+\d+\s+DE\s+|EXPORT[:\-]?\s*|RECEITA\s+NF\S*\s*[:\-]?\s*|INCL\s+TIT\s+AB\S*\s+DE\s+)?([A-Z0-9\s\.\-\/]+?(?:LTDA|S\/A|SA|LTD|Ltda|S.A.))",
    "Número do Título": r"(?i)(?:NF(?:E)?[:\- ]*)(\d{6,})",
    "Data de Emissão": r"(?i)EMISS(?:AO|ÃO)?[:\- ]+(\d{2}/\d{2}/\d{4})",
    "Data de Vencimento": r"(?i)VENC(?:TO|IMENTO)?[:\- ]+(\d{2}/\d{2}/\d{4})",
    "Valor do Título": r"(?i)VALOR[:\- R$]*([\d\.,]+)"
}

# Aplica uma expressão regular (regex) com fallback ao valor original

def aplicar_regex_com_fallback(df, coluna, regex):
    try:
        extraido = df[coluna].astype(str).str.extract(regex, expand=False)
        fallback = df[coluna].astype(str)
        return extraido.where(extraido.notnull(), fallback)
    except Exception as e:
        st.error(f"Erro ao aplicar regex na coluna '{coluna}': {e}")
        return df[coluna].astype(str)

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

    st.markdown("<div class='custom-subheader'>Visualização dos Dados Importados</div>", unsafe_allow_html=True)
    st.dataframe(df.head(5), use_container_width=True)

    st.markdown("<div class='custom-subheader'>Mapeamento dos Campos</div>", unsafe_allow_html=True)

    col_map_1, col_map_2, col_map_3, col_map_4, col_map_5 = st.columns(5)
    colunas_mapeamento = [col_map_1, col_map_2, col_map_3, col_map_4, col_map_5]

    for i, (campo, col) in enumerate(zip(CAMPOS_LOGICOS, colunas_mapeamento)):
        with col:
            st.markdown(f"**{campo}**")
            coluna_selecionada = st.selectbox("", colunas, key=f"sel_col_{i}")
            precisa_tratar = st.checkbox("Ajustar?", key=f"chk_regex_{i}", value=True)

        campos_mapeados[campo] = coluna_selecionada
        campos_com_tratamento[campo] = precisa_tratar

    df_resultado = pd.DataFrame()

    for campo, coluna in campos_mapeados.items():
        if campos_com_tratamento[campo]:
            regex = REGEX_SUGERIDA.get(campo, "")
            extraido = aplicar_regex_com_fallback(df, coluna, regex)

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

    # Converte e remove linhas com Data de Emissão inválida ou vazia
    if "Data de Emissão" in df_resultado.columns:
        df_resultado["Data de Emissão"] = pd.to_datetime(df_resultado["Data de Emissão"], errors="coerce", dayfirst=True)
        df_resultado = df_resultado[df_resultado["Data de Emissão"].notnull()]

    st.markdown("### Dados extraídos (tratados)")
    st.dataframe(df_resultado, use_container_width=True)

    st.session_state["df_titulos"] = df_resultado

    st.success("Extração concluída com sucesso.")
