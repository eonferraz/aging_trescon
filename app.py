import streamlit as st
import pandas as pd
import io
import re
from difflib import get_close_matches

st.set_page_config(page_title="Aging", layout="wide")

# Logo e título
st.markdown("""
    <div style="background-color: white; padding: 20px 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center; gap: 20px;">
            <img src="https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=304,fit=crop,q=95/Aq2B471lDpFnv1BK/logo---trescon-30-anos-mv0jg6Lo2EiV7yLp.png" style="height: 60px;">
            <h1 style="margin: 0; font-size: 2.4em;">Relatório de Aging - Conciliador</h1>
        </div>
    </div>
""", unsafe_allow_html=True)

# Upload de arquivos
with st.expander("1. Fonte de Dados", expanded=True):
    usar_arquivo_unico = st.checkbox("Usar o mesmo arquivo para Títulos e Baixas")
    if usar_arquivo_unico:
        arquivo_base = st.file_uploader("Arquivo Base (com uma ou mais abas)", type=["xlsx"], key="base")
        arquivo_extra = None
    else:
        col1, col2 = st.columns(2)
        with col1:
            arquivo_base = st.file_uploader("Arquivo de Títulos", type=["xlsx"], key="base")
        with col2:
            arquivo_extra = st.file_uploader("Arquivo de Baixas", type=["xlsx"], key="extra")

# Função para ler abas
def ler_abas(arquivo):
    if arquivo:
        xls = pd.ExcelFile(arquivo)
        return xls.sheet_names, xls
    return [], None

abas_base, xls_base = ler_abas(arquivo_base)
abas_extra, xls_extra = ler_abas(arquivo_extra)

# Regex de extração
regex_nf = r'NF[:\s]*(\d{5,})'
regex_cli = r'CLIENTE[:\s]*([A-Z0-9\s\-\/\&\.]+)'

def extrair_info(texto):
    doc = re.search(regex_nf, str(texto))
    forn = re.search(regex_cli, str(texto))
    return pd.Series([doc.group(1) if doc else None, forn.group(1).strip() if forn else None])

# Seleção de campos referenciais e pré-visualização
if xls_base:
    with st.expander("2. Seleção de Abas e Campos Referenciais", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            aba_tit = st.selectbox("Aba com Títulos", abas_base, key="aba_tit")
            df_tit = xls_base.parse(aba_tit)
            campo_tit = st.selectbox("Campo com descrição da NF (Títulos)", df_tit.columns)
            df_tit[['Documento', 'Fornecedor']] = df_tit[campo_tit].apply(extrair_info)
            col_valor_tit = st.selectbox("Coluna de Valor do Título", df_tit.columns)
            col_venc = st.selectbox("Coluna de Vencimento", df_tit.columns)
            col_emissao = st.selectbox("Coluna de Emissão", df_tit.columns)
            col_centro_custo = st.selectbox("Coluna de Centro de Custo", df_tit.columns)
            col_filial = st.selectbox("Coluna de Filial", df_tit.columns)
            st.dataframe(df_tit.head(), use_container_width=True)

        with col2:
            if usar_arquivo_unico:
                abas_opc = [a for a in abas_base if a != aba_tit]
                aba_baix = st.selectbox("Aba com Baixas", abas_opc, key="aba_baix")
                df_baix = xls_base.parse(aba_baix)
            else:
                aba_baix = st.selectbox("Aba com Baixas", abas_extra, key="aba_baix")
                df_baix = xls_extra.parse(aba_baix)
            campo_baix = st.selectbox("Campo com descrição da NF (Baixas)", df_baix.columns)
            df_baix[['Documento', 'Fornecedor']] = df_baix[campo_baix].apply(extrair_info)
            col_valor_baix = st.selectbox("Coluna de Valor Pago", df_baix.columns)
            col_data_pag = st.selectbox("Coluna de Data Pagamento", df_baix.columns)
            st.dataframe(df_baix.head(), use_container_width=True)

# Sugestões de melhoria:
# - Implementar lógica para identificação e tratamento de valores próximos, permitindo pequena variação na conciliação (e.g., tolerância percentual).
# - Adicionar opção para selecionar múltiplas colunas referenciais para agrupamento adicional, se necessário.
# - Integrar indicadores resumo após conciliação (percentual liquidado, pendências totais, etc.).
# - Avaliar uso de fuzzy matching para nomes de fornecedores caso haja necessidade posterior.
