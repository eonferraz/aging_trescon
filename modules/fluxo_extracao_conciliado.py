# modules/fluxo_extracao_conciliado.py
import streamlit as st
import pandas as pd
import re

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
    "Data de Emissão": r"(?i)EMISS(?:AO|\u00c3O)?[:\- ]+(\d{2}/\d{2}/\d{4})",
    "Data de Vencimento": r"(?i)VENC(?:TO|IMENTO)?[:\- ]+(\d{2}/\d{2}/\d{4})",
    "Valor do Título": r"(?i)VALOR[:\- R$]*([\d\.,]+)"
}

def aplicar_regex_em_coluna(df, coluna, regex):
    try:
        return df[coluna].astype(str).str.extract(regex, expand=False)
    except Exception as e:
        st.error(f"Erro ao aplicar regex na coluna '{coluna}': {e}")
        return None

def executar(df):
    if st.session_state.get("etapa") == "proxima_etapa":
        return

    if df.empty or df.shape[1] == 0:
        st.warning("Nenhum dado disponível para análise. Importe a conciliação anterior primeiro.")
        return

    colunas = df.columns.tolist()
    campos_mapeados = {}
    campos_com_tratamento = {}

    st.markdown("<div class='custom-subheader'>Visualização dos Dados Importados</div>", unsafe_allow_html=True)
    st.dataframe(df.head(5), use_container_width=True)

    st.markdown("<div class='custom-subheader'>Mapeamento dos Campos da Conciliação Anterior</div>", unsafe_allow_html=True)
    col_map = st.columns(len(CAMPOS_LOGICOS))

    for i, (campo, col) in enumerate(zip(CAMPOS_LOGICOS, col_map)):
        with col:
            st.markdown(f"**{campo}**")
            coluna_selecionada = st.selectbox("", colunas, key=f"sel_col_conc_{i}")
            precisa_tratar = st.checkbox("Ajustar?", key=f"chk_regex_conc_{i}", value=True)

        campos_mapeados[campo] = coluna_selecionada
        campos_com_tratamento[campo] = precisa_tratar

    df_resultado = pd.DataFrame()

    for campo, coluna in campos_mapeados.items():
        if campos_com_tratamento[campo]:
            regex = REGEX_SUGERIDA.get(campo, "")
            extraido = aplicar_regex_em_coluna(df, coluna, regex)

            if campo == "Número do Título":
                df_resultado[campo] = (
                    extraido.fillna(df[coluna])
                    .astype(str)
                    .str.replace(".0", "", regex=False)
                    .str.strip()
                    .str.zfill(9)
                )
            else:
                df_resultado[campo] = extraido.fillna(df[coluna])
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

    # ✅ Correção do erro: garante que a coluna seja string válida
    df_resultado = df_resultado[
        df_resultado["Data de Emissão"]
        .astype(str)
        .str.strip()
        .replace("nan", "")
        .str.len() > 0
    ]

    st.markdown("### Dados extraídos da Conciliação Anterior")
    st.dataframe(df_resultado, use_container_width=True)

    st.session_state["df_conciliado_bruto"] = df_resultado

    st.success("Extração da conciliação anterior concluída com sucesso.")
