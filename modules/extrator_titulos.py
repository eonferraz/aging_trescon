import streamlit as st
import pandas as pd
import re

# Campos possíveis para extração
CAMPOS_DISPONIVEIS = [
    "Fornecedor",
    "Número do Título",
    "Data de Emissão",
    "Data de Vencimento",
    "Valor do Título"
]

# Regex sugerido por campo
REGEX_SUGERIDA = {
    "Fornecedor": r"(?i)CLIENTE[:\- ]+\s*(.+)",
    "Número do Título": r"(?i)NF[:\- ]+(\d+)",
    "Data de Emissão": r"(?i)EMISS(?:AO|ÃO)?[:\- ]+(\d{2}/\d{2}/\d{4})",
    "Data de Vencimento": r"(?i)VENC(?:TO|IMENTO)?[:\- ]+(\d{2}/\d{2}/\d{4})",
    "Valor do Título": r"(?i)VALOR[:\- R$]*([\d\.,]+)"
}


def aplicar_regex_em_coluna(df, coluna, regex):
    """
    Aplica a regex na coluna selecionada e retorna os dados extraídos.
    """
    try:
        return df[coluna].astype(str).str.extract(regex, expand=False)
    except Exception as e:
        st.error(f"Erro ao aplicar regex: {e}")
        return None


def executar(df):
    """
    Interface assistida para extrair campos de colunas com texto livre.
    O usuário escolhe o campo desejado e o sistema analisa as colunas automaticamente.
    """
    st.markdown("<div class='custom-subheader'>🧠 Extração Assistida de Campos</div>", unsafe_allow_html=True)

    if df.empty or df.shape[1] == 0:
        st.warning("Nenhum dado disponível para análise. Importe os títulos primeiro.")
        return

    campo = st.selectbox("Selecione o campo que deseja extrair:", CAMPOS_DISPONIVEIS)
    regex = REGEX_SUGERIDA.get(campo, "")

    colunas_texto = df.select_dtypes(include='object').columns.tolist()

    if not colunas_texto:
        st.warning("Não foram encontradas colunas com texto para análise.")
        return

    st.markdown("### 🔎 Análise automática das colunas disponíveis")

    for col in colunas_texto:
        # Aplica o regex à coluna
        extraido = aplicar_regex_em_coluna(df, col, regex)

        if extraido is not None and extraido.notna().sum() > 0:
            st.markdown(f"**Coluna:** `{col}` — valores extraídos encontrados:")
            preview = pd.DataFrame({
                "Texto Original": df[col].head(5),
                f"{campo} Extraído": extraido.head(5)
            })
            st.dataframe(preview, use_container_width=True)

            if st.button(f"✅ Usar coluna '{col}' para '{campo}'"):
                df_resultado = df.copy()
                df_resultado[campo] = extraido
                st.session_state[f"campo_extraido_{campo.lower().replace(' ', '_')}"] = extraido
                st.session_state["df_titulos"] = df_resultado
                st.success(f"Campo '{campo}' extraído e salvo com sucesso usando a coluna '{col}'.")

        else:
            st.markdown(f"<span style='color: #bbb;'>Coluna `{col}` → nenhum valor extraído.</span>", unsafe_allow_html=True)
