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
    "Número do Título": r"(?i)(?:NF(?:E)?[:\- ]*|Ref NF |CF NF[:\- ]*|RECEITA NF(?: EXPORT)?: |DEV NF |NF[:\- ]*)(\d{6,})",
    "Data da Baixa": r"(?i)(\d{2}/\d{2}/\d{4})",
    "Valor da Baixa": r"(?i)VALOR[:\- R$]*([\d\.,]+)",
    "Documento": r"(?i)DOC[:\-\s]*([\w/\\-]+)",
    "Conta": r"(?i)CONTA[:\-\s]*(.+)",
    "Cliente": r"(?i)CLIENTE[:\- ]*(.+)"  # exemplo adicional
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
    
    #---------------------------------------------------------------------------------------------------------------------
    #st.markdown("---")
    st.markdown("<div class='custom-subheader'>Visualização dos Dados Importados</div>", unsafe_allow_html=True)
    st.dataframe(df.head(5), use_container_width=True)
    
    st.markdown("<div class='custom-subheader'>Mapeamento dos Campos</div>", unsafe_allow_html=True)

    col_map_1, col_map_2, col_map_3, col_map_4, col_map_5 = st.columns(5)
    colunas_mapeamento = [col_map_1, col_map_2, col_map_3, col_map_4, col_map_5]

    campos_mapeados = {}
    campos_com_tratamento = {}

    for i, (campo, col) in enumerate(zip(CAMPOS_LOGICOS, colunas_mapeamento)):
        with col:
            st.markdown(f"**{campo}**")
            coluna_selecionada = st.selectbox("", colunas, key=f"sel_col_{i}")
            precisa_tratar = st.checkbox("Ajustar?", key=f"chk_regex_{i}", value=True)

        campos_mapeados[campo] = coluna_selecionada
        campos_com_tratamento[campo] = precisa_tratar    
    #---------------------------------------------------------------------------------------------------------------------
   
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
                
    #st.markdown("---")
    st.markdown("### Dados extraídos (tratados)")
    st.dataframe(df_resultado, use_container_width=True)
    
    st.session_state["df_titulos"] = df_resultado
    
    st.success("Extração concluída com sucesso.")

    # Exibe botão para avançar de etapa        
    # if st.button("➡️ Próximo"):
    #     if "extracao_titulos" not in st.session_state["etapas_concluidas"]:
    #         st.session_state["etapas_concluidas"].append("extracao_titulos")
    #     st.experimental_rerun()

