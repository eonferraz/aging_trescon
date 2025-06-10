import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Conciliador de Fornecedores", layout="wide")
st.title("🔍 Conciliador de Fornecedores")

# --- ARQUIVOS ---
st.header("1. Fonte de Dados")
usar_arquivo_unico = st.checkbox("Usar o mesmo arquivo para Títulos e Baixas")

arquivo_base = st.file_uploader("Arquivo Base (com uma ou mais abas)", type=["xlsx"])
arquivo_extra = None
if not usar_arquivo_unico:
    arquivo_extra = st.file_uploader("Arquivo Secundário (caso abas estejam em arquivos separados)", type=["xlsx"])

def ler_abas(arquivo):
    if arquivo:
        xls = pd.ExcelFile(arquivo)
        return xls.sheet_names, xls
    return [], None

abas_base, xls_base = ler_abas(arquivo_base)
abas_extra, xls_extra = ler_abas(arquivo_extra)

if xls_base:
    aba_titulos = st.selectbox("Aba com Títulos", abas_base, key="aba_titulos")
    df_tit = xls_base.parse(aba_titulos)

    if usar_arquivo_unico:
        aba_baixas = st.selectbox("Aba com Baixas", [a for a in abas_base if a != aba_titulos], key="aba_baixas")
        df_baix = xls_base.parse(aba_baixas)
    elif xls_extra:
        aba_baixas = st.selectbox("Aba com Baixas", abas_extra, key="aba_baixas")
        df_baix = xls_extra.parse(aba_baixas)
    else:
        st.warning("Por favor, selecione ou carregue o arquivo de baixas.")
        st.stop()

    # --- VISUALIZAÇÃO LADO A LADO ---
    st.subheader("Prévia dos Dados")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Títulos:**")
        st.dataframe(df_tit.head())
    with col2:
        st.write("**Baixas:**")
        st.dataframe(df_baix.head())

    # --- EXTRAÇÃO INTELIGENTE ---
    st.header("2. Extração de Documento e Fornecedor")
    usar_extracao = st.checkbox("Extrair dados de campo combinado?")

    if usar_extracao:
        campo_combinado = st.selectbox("Selecione o campo combinado", df_tit.columns)

        def extrair_info(texto):
            try:
                doc = re.search(r'NF[:\s]*(\d+)', str(texto)).group(1)
                forn = re.search(r'CLIENTE[:\s]*(.*)', str(texto)).group(1)
                return pd.Series([doc, forn])
            except:
                return pd.Series([None, None])

        df_tit[['Documento', 'Fornecedor']] = df_tit[campo_combinado].apply(extrair_info)
    else:
        col_doc_tit = st.selectbox("Coluna de Documento - Títulos", df_tit.columns)
        col_forn_tit = st.selectbox("Coluna de Fornecedor - Títulos", df_tit.columns)
        df_tit['Documento'] = df_tit[col_doc_tit]
        df_tit['Fornecedor'] = df_tit[col_forn_tit]

    col_doc_baix = st.selectbox("Coluna de Documento - Baixas", df_baix.columns)
    col_forn_baix = st.selectbox("Coluna de Fornecedor - Baixas", df_baix.columns)
    col_valor_baix = st.selectbox("Coluna de Valor Pago", df_baix.columns)
    col_data_baix = st.selectbox("Coluna de Data de Pagamento", df_baix.columns)

    df_baix['Documento'] = df_baix[col_doc_baix]
    df_baix['Fornecedor'] = df_baix[col_forn_baix]
    df_baix['Valor Pago'] = pd.to_numeric(df_baix[col_valor_baix], errors='coerce')
    df_baix['Data Pagamento'] = pd.to_datetime(df_baix[col_data_baix], errors='coerce')

    # --- CONCILIAÇÃO ---
    st.header("3. Conciliação")
    col_valor_tit = st.selectbox("Coluna de Valor do Título", df_tit.columns)
    col_data_emissao = st.selectbox("Coluna de Emissão", df_tit.columns)
    col_data_venc = st.selectbox("Coluna de Vencimento", df_tit.columns)

    df_tit['Valor Título'] = pd.to_numeric(df_tit[col_valor_tit], errors='coerce')
    df_tit['Data Emissão'] = pd.to_datetime(df_tit[col_data_emissao], errors='coerce')
    df_tit['Vencimento'] = pd.to_datetime(df_tit[col_data_venc], errors='coerce')

    pagamentos_agrupados = df_baix.groupby(['Documento', 'Fornecedor']).agg({
        'Valor Pago': 'sum'
    }).reset_index()

    df_conc = pd.merge(df_tit, pagamentos_agrupados, on=['Documento', 'Fornecedor'], how='left')
    df_conc['Valor Pago'] = df_conc['Valor Pago'].fillna(0)
    df_conc['Diferença'] = df_conc['Valor Título'] - df_conc['Valor Pago']

    def classificar(row):
        if row['Valor Pago'] == 0:
            return 'Em Aberto'
        elif abs(row['Diferença']) < 1:
            return 'Liquidado'
        elif row['Valor Pago'] > row['Valor Título']:
            return 'Valor Divergente'
        else:
            return 'Parcialmente Pago'

    df_conc['Status'] = df_conc.apply(classificar, axis=1)

    # --- OUTPUT PRINCIPAL ---
    st.subheader("Resultado da Conciliação")
    st.dataframe(df_conc)

    # --- EXPORTAÇÃO ---
    st.header("4. Exportação")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_conc.to_excel(writer, sheet_name='Conciliação', index=False)
    st.download_button(
        label="📥 Baixar Resultado em Excel",
        data=buffer.getvalue(),
        file_name="consolidado_conciliacao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
