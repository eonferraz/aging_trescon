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

#Aplicar regex
def aplicar_regex_em_coluna(df, coluna, regex):
    """
    Aplica uma expressão regular (regex) à coluna do DataFrame e retorna os dados extraídos.
    """
    try:
        return df[coluna].astype(str).str.extract(regex, expand=False)
    except Exception as e:
        st.error(f"Erro ao aplicar regex na coluna '{coluna}': {e}")
        return None




#Função
def executar(df):
    #st.markdown("<div class='custom-subheader'>🧠 Mapeamento e Extração Assistida de Campos</div>", unsafe_allow_html=True)

    if df.empty or df.shape[1] == 0:
        st.warning("Nenhum dado disponível para análise. Importe os títulos primeiro.")
        return

    colunas = df.columns.tolist()
    campos_mapeados = {}
    campos_com_tratamento = {}
    campos_ref = {}

    # Layout em duas colunas
    col_esq, col_dir = st.columns([3, 2])

    with col_esq:
        st.markdown("<div class='custom-subheader'>Visuaização dos Dados Importados</div>", unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)

    with col_dir:
        st.markdown("<div class='custom-subheader'>Mapeamento dos Campos</div>", unsafe_allow_html=True)
        for campo in CAMPOS_LOGICOS:
            campos, sel_col, chk = st.columns([2, 2, 1])
    
            with campos:
                st.markdown(f"`{campo}`")
    
            with sel_col:
                coluna_selecionada = st.selectbox(
                    "",
                    colunas,
                    key=f"sel_col_{campo}"
                )
    
            with chk:
                precisa_tratar = st.checkbox("Regex?", key=f"chk_regex_{campo}", value=True)
    
            campos_mapeados[campo] = coluna_selecionada
            campos_com_tratamento[campo] = precisa_tratar

    # Aplicação de extrações ou cópias diretas
    st.markdown("---")
    st.markdown("### ✨ Resultados das Extrações")

    df_resultado = df.copy()

    extracoes = []  # Lista para armazenar os resultados extraídos

    for campo, coluna in campos_mapeados.items():
        if coluna not in df.columns:
            continue
    
        textos_originais = df[coluna].astype(str)
    
        if campos_com_tratamento[campo]:
            regex = REGEX_SUGERIDA.get(campo, "")
            extraidos = aplicar_regex_em_coluna(df, coluna, regex)
    
            for i, (texto, valor) in enumerate(zip(textos_originais, extraidos)):
                extracoes.append({
                    "Linha": i + 1,
                    "Campo": campo,
                    "Coluna Origem": coluna,
                    "Texto Original": texto,
                    "Valor Extraído": valor if pd.notna(valor) else "",
                    "Tratado com Regex": True
                })
    
        else:
            for i, texto in enumerate(textos_originais):
                extracoes.append({
                    "Linha": i + 1,
                    "Campo": campo,
                    "Coluna Origem": coluna,
                    "Texto Original": texto,
                    "Valor Extraído": texto,
                    "Tratado com Regex": False
                })
    
    # Cria DataFrame com todos os resultados organizados
    df_extracoes = pd.DataFrame(extracoes)
    st.markdown("### 📄 Resultado consolidado das extrações")
    st.dataframe(df_extracoes, use_container_width=True)
    
    # Salva no session_state para exportação futura
    st.session_state["df_extracoes"] = df_extracoes


    st.session_state["df_titulos"] = df_resultado
    st.markdown("---")
    st.success("✅ Mapeamento e tratamento concluídos. Dados prontos para conciliação ou exportação.")
