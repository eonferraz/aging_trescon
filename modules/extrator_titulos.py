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
    "Fornecedor": r"(?i)CLIENTE[:\- ]+\s*(.+)",
    "Número do Título": r"(?i)NF[:\- ]+(\d+)",
    "Data de Emissão": r"(?i)EMISS(?:AO|ÃO)?[:\- ]+(\d{2}/\d{2}/\d{4})",
    "Data de Vencimento": r"(?i)VENC(?:TO|IMENTO)?[:\- ]+(\d{2}/\d{2}/\d{4})",
    "Valor do Título": r"(?i)VALOR[:\- R$]*([\d\.,]+)"
}

def aplicar_regex_em_coluna(df, coluna, regex):
    """Aplica regex e retorna valores extraídos"""
    try:
        return df[coluna].astype(str).str.extract(regex, expand=False)
    except Exception as e:
        st.error(f"Erro ao aplicar regex: {e}")
        return None

def executar(df):
    """
    Interface assistida para mapeamento e tratamento de colunas do DataFrame.
    O usuário escolhe qual coluna representa cada campo lógico e se precisa de regex.
    """
    st.markdown("<div class='custom-subheader'>🧠 Mapeamento e Extração Assistida de Campos</div>", unsafe_allow_html=True)

    if df.empty or df.shape[1] == 0:
        st.warning("Nenhum dado disponível para análise. Importe os títulos primeiro.")
        return

    st.markdown("### 🧾 Visualização dos Dados Importados")
    st.dataframe(df.head(10), use_container_width=True)

    colunas = df.columns.tolist()
    campos_mapeados = {}
    campos_com_tratamento = {}

    st.markdown("### 🛠️ Mapeamento de Campos")

    # Loop por cada campo lógico (Fornecedor, NF, etc.)
    for campo in CAMPOS_LOGICOS:
        st.markdown(f"**Campo lógico:** `{campo}`")

        col, col2 = st.columns([2, 1])
        with col:
            coluna_selecionada = st.selectbox(
                f"→ Qual coluna contém o campo '{campo}'?",
                colunas,
                key=f"sel_col_{campo}"
            )
        with col2:
            precisa_tratar = st.checkbox("Tratar via regex?", key=f"chk_regex_{campo}", value=True)

        campos_mapeados[campo] = coluna_selecionada
        campos_com_tratamento[campo] = precisa_tratar

    # Inicializa DataFrame resultado
    df_resultado = df.copy()

    st.markdown("---")
    st.markdown("### ✨ Resultados das Extrações")

    for campo, coluna in campos_mapeados.items():
        if campos_com_tratamento[campo]:
            regex = REGEX_SUGERIDA.get(campo, "")

            extraido = aplicar_regex_em_coluna(df, coluna, regex)

            if extraido is not None and extraido.notna().sum() > 0:
                df_resultado[campo] = extraido
                st.success(f"Campo '{campo}' extraído com sucesso da coluna '{coluna}'")
                st.dataframe(
                    pd.DataFrame({
                        "Texto Original": df[coluna].head(5),
                        f"{campo} Extraído": extraido.head(5)
                    }),
                    use_container_width=True
                )
            else:
                st.warning(f"Não foi possível extrair '{campo}' da coluna '{coluna}' com a regex padrão.")
        else:
            # Apenas copia o valor diretamente da coluna escolhida
            df_resultado[campo] = df[coluna]
            st.info(f"Campo '{campo}' definido diretamente da coluna '{coluna}' (sem regex).")
            st.dataframe(df[[coluna]].head(5).rename(columns={coluna: campo}), use_container_width=True)

    # Salva resultado no session_state
    st.session_state["df_titulos"] = df_resultado

    st.markdown("---")
    st.success("✅ Mapeamento e tratamento concluídos. Dados prontos para conciliação ou exportação.")
