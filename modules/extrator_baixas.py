import streamlit as st
import pandas as pd
import re

# Campos a extrair/tratar nas baixas financeiras
CAMPOS_BAIXAS = [
    "Número do Título",
    "Data da Baixa",
    "Valor da Baixa",
    "Documento",
    "Conta"
]

# Regex sugerido (pode ser adaptado conforme os padrões dos arquivos reais)
REGEX_SUGERIDA_BAIXAS = {
    "Número do Título": r"(?i)(?:NF(?:E)?[:\- ]*)(\d{6,})",
    "Data da Baixa": r"(?i)(\d{2}/\d{2}/\d{4})",
    "Valor da Baixa": r"(?i)VALOR[:\- R$]*([\d\.,]+)",
    "Documento": r"(?i)DOC[:\-\s]*([\w/\\-]+)",
    "Conta": r"(?i)CONTA[:\-\s]*(.+)"
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
        st.warning("Nenhum dado disponível para as baixas. Importe os dados primeiro.")
        return

    colunas = df.columns.tolist()
    campos_mapeados = {}
    campos_com_tratamento = {}

    st.markdown("<div class='custom-subheader'>Mapeamento de Campos - Baixas</div>", unsafe_allow_html=True)
    for i, campo in enumerate(CAMPOS_BAIXAS):
        campos, sel_col, chk = st.columns([2, 2, 1], gap="small")

        with campos:
            st.markdown(f"`{campo}`")

        with sel_col:
            coluna_selecionada = st.selectbox(
                f"Coluna para {campo}",
                colunas,
                key=f"sel_col_baixa_{i}"
            )

        with chk:
            precisa_tratar = st.checkbox("Regex?", key=f"chk_regex_baixa_{i}", value=True)

        campos_mapeados[campo] = coluna_selecionada
        campos_com_tratamento[campo] = precisa_tratar

    st.markdown("---")
    df_resultado = pd.DataFrame()

    for campo, coluna in campos_mapeados.items():
        if campos_com_tratamento[campo]:
            regex = REGEX_SUGERIDA_BAIXAS.get(campo, "")
            extraido = aplicar_regex_em_coluna(df, coluna, regex)
            df_resultado[campo] = extraido.fillna("")
        else:
            df_resultado[campo] = df[coluna].fillna("")

    st.markdown("### Baixas tratadas")
    st.dataframe(df_resultado, use_container_width=True)

    st.session_state["df_baixas"] = df_resultado
    st.success("Extração das baixas concluída com sucesso.")

    if st.button("\u27a1\ufe0f Próximo"):
        st.session_state["etapa"] = "conciliacao"
        st.experimental_rerun()

    st.markdown("---")
