import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Aging", layout="wide")
#------------------------------------------------------------------------------------------------------------------------------------------------------
# Logo + título lado a lado
st.markdown(
    """
    <div style="background-color: white; padding: 20px 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center; gap: 20px;">
            <img src="https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=304,fit=crop,q=95/Aq2B471lDpFnv1BK/logo---trescon-30-anos-mv0jg6Lo2EiV7yLp.png" style="height: 60px;">
            <h1 style="margin: 0; font-size: 2.4em;">Relatório de Aging - Conciliador</h1>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.title("🔍 Conciliador de Fornecedores")

# --- ARQUIVOS ---
st.header("1. Fonte de Dados")
usar_arquivo_unico = st.checkbox("Usar o mesmo arquivo para Títulos e Baixas")

if usar_arquivo_unico:
    arquivo_base = st.file_uploader("Arquivo Base (com uma ou mais abas)", type=["xlsx"], key="base")
    arquivo_extra = None
else:
    col1, col2 = st.columns(2)
    with col1:
        arquivo_base = st.file_uploader("Arquivo de Títulos", type=["xlsx"], key="base")
    with col2:
        arquivo_extra = st.file_uploader("Arquivo de Baixas", type=["xlsx"], key="extra")st.file_uploader("Arquivo Secundário (caso abas estejam em arquivos separados)", type=["xlsx"], key="extra")

def ler_abas(arquivo):
    if arquivo:
        xls = pd.ExcelFile(arquivo)
        return xls.sheet_names, xls
    return [], None

abas_base, xls_base = ler_abas(arquivo_base)
abas_extra, xls_extra = ler_abas(arquivo_extra)

if xls_base:
    st.subheader("2. Seleção de Abas e Pré-visualização")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Títulos")
        aba_titulos = st.selectbox("Aba com Títulos", abas_base, key="aba_titulos")
        df_tit = xls_base.parse(aba_titulos)
        st.dataframe(df_tit.head())
    with col2:
        st.markdown("### Baixas")
        if usar_arquivo_unico:
            abas_opcoes = [a for a in abas_base if a != aba_titulos]
            aba_baixas = st.selectbox("Aba com Baixas", abas_opcoes, key="aba_baixas")
            df_baix = xls_base.parse(aba_baixas)
        elif xls_extra:
            aba_baixas = st.selectbox("Aba com Baixas", abas_extra, key="aba_baixas")
            df_baix = xls_extra.parse(aba_baixas)
        else:
            st.warning("Por favor, selecione ou carregue o arquivo de baixas.")
            st.stop()
        st.dataframe(df_baix.head())

    col1, col2 = st.columns(2)
    with col1:
        usar_extracao = st.checkbox("Extrair Documento e Fornecedor de campo combinado?", key="extrair_tit")
        if usar_extracao:
            campo_combinado = st.selectbox("Campo combinado (Títulos)", df_tit.columns)
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
        col_valor_tit = st.selectbox("Coluna de Valor do Título", df_tit.columns)
        col_data_emissao = st.selectbox("Coluna de Emissão", df_tit.columns)
        col_data_venc = st.selectbox("Coluna de Vencimento", df_tit.columns)
    with col2:
        col_doc_baix = st.selectbox("Coluna de Documento - Baixas", df_baix.columns)
        col_forn_baix = st.selectbox("Coluna de Fornecedor - Baixas", df_baix.columns)
        col_valor_baix = st.selectbox("Coluna de Valor Pago", df_baix.columns)
        col_data_baix = st.selectbox("Coluna de Data de Pagamento", df_baix.columns)

    # --- TRATAMENTO ---
    df_tit['Documento'] = df_tit['Documento'].astype(str).str.strip()
    df_tit['Fornecedor'] = df_tit['Fornecedor'].astype(str).str.strip()
    df_tit['Valor Título'] = pd.to_numeric(df_tit[col_valor_tit], errors='coerce')
    df_tit['Data Emissão'] = pd.to_datetime(df_tit[col_data_emissao], errors='coerce').dt.strftime('%d/%m/%Y')
    df_tit['Vencimento'] = pd.to_datetime(df_tit[col_data_venc], errors='coerce').dt.strftime('%d/%m/%Y')

    df_baix['Documento'] = df_baix[col_doc_baix].astype(str).str.strip()
    df_baix['Fornecedor'] = df_baix[col_forn_baix].astype(str).str.strip()
    df_baix['Valor Pago'] = pd.to_numeric(df_baix[col_valor_baix], errors='coerce')
    df_baix['Valor Pago Formatado'] = df_baix['Valor Pago'].map(lambda x: f"R$ {x:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
    df_baix['Data Pagamento'] = pd.to_datetime(df_baix[col_data_baix], errors='coerce').dt.strftime('%d/%m/%Y')

    # --- CONCILIAÇÃO ---
    st.header("3. Conciliação")
    pagamentos_agrupados = df_baix.groupby(['Documento', 'Fornecedor']).agg({
        'Valor Pago': 'sum'
    }).reset_index()

    pagamentos_agrupados['Documento'] = pagamentos_agrupados['Documento'].astype(str).str.strip()
    pagamentos_agrupados['Fornecedor'] = pagamentos_agrupados['Fornecedor'].astype(str).str.strip()

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
    df_conc['Valor Título'] = df_conc['Valor Título'].map(lambda x: f"R$ {x:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
    df_conc['Valor Pago'] = df_conc['Valor Pago'].map(lambda x: f"R$ {x:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
    df_conc['Diferença'] = df_conc['Diferença'].map(lambda x: f"R$ {x:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))

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
