# extrator_baixas.py
import streamlit as st
import pandas as pd
import re
import os

# Campos esperados para extração
CAMPOS_BAIXAS = [
    "Fornecedor/Cliente",
    "Número do Título",
    "Data de Pagamento",
    "Valor Pago"
]

# Regex sugerida para cada campo
REGEX_SUGERIDA = {
    # Fornecedor/Cliente
    "Fornecedor/Cliente": r"(?i)(?:COMPENS\s+ADTO\s+CLIENTE\s+REF\s+NF\s+\d+\s+NF\s+\d+-\s*|COMPENS\s+ADTO\s+CLIENTE\s+Ref\s+NF\s+\d+\s+NCC\d{2}-\s*|DEV\s+NF\s+\d+\s+CF\s+NF\s+\d+\s+DE\s+|CLIENTE[:\-]?\s*|DE\s+|NF\s+\d+\s+DE\s+|CF\s+NF\s+\d+\s+DE\s+|Ref\s+NF\s+\d+\s+NF\s+\d+[- ]*)?([A-Z0-9\s\.\-/]+?(?:LTDA|LTD|S/A|SA|S\.A\.|Ltda|Automoveis|AUTOM|SUCATA|MATTEO|BRASIL|RENAULT|PEUGEOT|CITROEN))",

    # Número do Título
    "Número do Título": r"(?i)(?:COMPENS\s+ADTO\s+CLIENTE\s+REF\s+NF\s+|COMPENS\s+ADTO\s+CLIENTE\s+Ref\s+NF\s+|NF[:\- ]*|NFE[:\- ]*|REF\s*NF\s*|CF\s*NF\s*|TIT\s*AB[-\s]*|EXPORT[:\- ]*|SERV[:\- ]*|RECEITA\s+NF[:\- ]*|INCL\s+TIT\s+AB[-\s]*\d*\s*[-]?)?(\d{5,})",

    # Data de Pagamento (data final do texto)
    "Data de Pagamento": r"(?i)(\d{2}/\d{2}/\d{2,4})$",

    # Valor Pago
    "Valor Pago": r"(?i)VALOR[:\- R$]*([\d\.,]+)"
}

# Carrega de-para de fornecedores
CAMINHO_DEPARA = "depara.xlsx"
DEPARA_FORNECEDORES = {}
if os.path.exists(CAMINHO_DEPARA):
    try:
        df_depara = pd.read_excel(CAMINHO_DEPARA, dtype=str)
        DEPARA_FORNECEDORES = dict(zip(df_depara['de'].str.upper().str.strip(), df_depara['para'].str.strip()))
    except Exception as e:
        st.warning(f"Erro ao carregar de-para de fornecedores: {e}")

def aplicar_regex_em_coluna(df, coluna, regex):
    try:
        return df[coluna].astype(str).str.extract(regex, expand=False)
    except Exception as e:
        st.error(f"Erro ao aplicar regex na coluna '{coluna}': {e}")
        return None

def limpar_fornecedor(texto):
    texto = re.sub(r"\\bNFE\\b", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\\bCLIENTE:\s*", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\\bDE\\b", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\\b\d{1,6}\\b", "", texto)  # Remove números de até 6 dígitos isolados
    texto = texto.strip().upper()
    return DEPARA_FORNECEDORES.get(texto, texto)

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
            regex = REGEX_SUGERIDA.get(campo, "")
            extraido = aplicar_regex_em_coluna(df, coluna, regex).fillna("").astype(str).str.strip()
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
            valores_finais = valores_finais.str.strip()
            valores_finais = valores_finais.apply(lambda x: x.replace(".", "").replace(",", ".") if "," in x else x)
            valores_convertidos = pd.to_numeric(valores_finais, errors="coerce")
            df_resultado[campo] = valores_convertidos.round(2)
        elif campo == "Data de Pagamento":
            df_resultado[campo] = pd.to_datetime(valores_finais, errors="coerce", dayfirst=True)
        elif campo == "Fornecedor/Cliente":
            df_resultado[campo] = valores_finais.apply(limpar_fornecedor)
        else:
            df_resultado[campo] = valores_finais

    # Remove registros sem data de pagamento
    df_resultado = df_resultado[df_resultado["Data de Pagamento"].notna()].reset_index(drop=True)

    st.dataframe(df_resultado, use_container_width=True)
    st.session_state["df_baixas"] = df_resultado
