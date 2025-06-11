import streamlit as st
import pandas as pd
import re

# Lista de campos que o usuário pode extrair dos textos livres
CAMPOS_DISPONIVEIS = [
    "Fornecedor",
    "Número do Título",
    "Data de Emissão",
    "Data de Vencimento",
    "Valor do Título"
]

# Sugestões de expressões regulares por campo (o usuário pode editar depois)
REGEX_SUGERIDA = {
    "Fornecedor": r"CLIENTE[:\- ]+(.+)",
    "Número do Título": r"NF[:\- ]+(\d+)",
    "Data de Emissão": r"EMISSÃO[:\- ]+(\d{2}/\d{2}/\d{4})",
    "Data de Vencimento": r"VENC[:\- ]+(\d{2}/\d{2}/\d{4})",
    "Valor do Título": r"VALOR[:\- R$]*([\d\.,]+)"
}


def aplicar_regex_em_coluna(df, coluna_origem, regex):
    """
    Aplica uma expressão regular em uma coluna e retorna os valores extraídos.

    Args:
        df (pd.DataFrame): DataFrame original
        coluna_origem (str): Nome da coluna onde será aplicada a extração
        regex (str): Expressão regular definida pelo usuário

    Returns:
        pd.Series: Série com os dados extraídos ou None caso erro
    """
    try:
        return df[coluna_origem].astype(str).str.extract(regex, expand=False)
    except Exception as e:
        st.error(f"Erro ao aplicar regex: {e}")
        return None


def executar(df):
    """
    Função principal do módulo. Permite ao usuário selecionar uma coluna de texto livre,
    escolher qual campo deseja extrair (ex: Fornecedor), definir ou ajustar a regex, 
    e visualizar o resultado da extração com opção de correção manual.

    Args:
        df (pd.DataFrame): DataFrame original com os dados importados dos títulos
    """
    st.markdown("<div class='custom-subheader'>🔍 Extração de Campos dos Títulos</div>", unsafe_allow_html=True)

    # Verifica se há colunas no DataFrame
    if df.empty or df.shape[1] == 0:
        st.warning("Nenhum dado disponível para análise. Importe os títulos primeiro.")
        return

    # Seleção do campo que o usuário deseja extrair
    campo = st.selectbox("Qual campo deseja extrair?", CAMPOS_DISPONIVEIS)

    # Seleção da coluna onde a informação está embutida
    coluna_origem = st.selectbox("Selecione a coluna que contém os dados misturados:", df.columns)

    # Sugestão automática de regex baseada no campo escolhido
    regex_default = REGEX_SUGERIDA.get(campo, "")

    # Permitir ao usuário ajustar a expressão regular
    regex = st.text_input("Digite a expressão regular (regex) para extrair o valor desejado:", value=regex_default)

    # Exibir exemplo de conteúdo da coluna selecionada
    st.markdown("#### 🧾 Exemplos da Coluna Selecionada")
    st.dataframe(df[[coluna_origem]].head(10), use_container_width=True)

    # Botão para aplicar regex
    if st.button("🔍 Aplicar Extração"):
        extraido = aplicar_regex_em_coluna(df, coluna_origem, regex)

        if extraido is not None:
            df_resultado = df.copy()
            df_resultado[campo] = extraido

            st.success(f"Campo '{campo}' extraído com sucesso! Você pode revisar e editar abaixo.")
            st.data_editor(df_resultado[[coluna_origem, campo]].head(20), use_container_width=True)

            # Armazena no session_state para reutilização posterior
            chave = f"campo_extraido_{campo.lower().replace(' ', '_')}"
            st.session_state[chave] = df_resultado[campo]

            # Se desejar armazenar o DataFrame completo com a nova coluna:
            st.session_state["df_titulos"] = df_resultado

