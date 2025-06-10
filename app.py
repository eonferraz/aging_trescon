import streamlit as st
import pandas as pd
import io
import re
import difflib

st.set_page_config(page_title="Aging", layout="wide")

# Modularização de funções
def extrair_info(texto):
    try:
        doc = re.search(r'NF[:\s]*(\d+)', str(texto)).group(1)
        forn = re.search(r'CLIENTE[:\s]*(.*)', str(texto)).group(1)
        return pd.Series([doc, forn])
    except:
        return pd.Series([None, None])

def extrair_forn_similar(texto, fornecedores):
    melhores = difflib.get_close_matches(str(texto), fornecedores, n=1, cutoff=0.4)
    return melhores[0] if melhores else None

def ler_arquivo(arquivo):
    if arquivo:
        return pd.ExcelFile(arquivo)
    return None

def processar_conciliacao(df_tit, df_baix, colunas):
    pagamentos_agrupados = df_baix.groupby('Documento')[colunas['valor_baix']].sum().reset_index().rename(columns={colunas['valor_baix']: 'Valor Pago'})

    df_conc = pd.merge(df_tit, pagamentos_agrupados, on='Documento', how='left')
    df_conc['Valor Pago'] = df_conc['Valor Pago'].fillna(0)
    df_conc['Diferença'] = df_conc[colunas['valor_tit']] - df_conc['Valor Pago']
    df_conc['Status Conciliação'] = df_conc['Diferença'].apply(lambda x: 'Liquidado' if abs(x) < 0.01 else 'Pendente')

    return df_conc

# Interface
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

# Fonte de Dados
with st.expander("1. Fonte de Dados", expanded=True):
    usar_arquivo_unico = st.checkbox("Usar o mesmo arquivo para Títulos e Baixas")
    col1, col2 = st.columns(2)
    with col1:
        arquivo_base = st.file_uploader("Arquivo Base ou Títulos", type=["xlsx"], key="base")
    with col2:
        arquivo_extra = None if usar_arquivo_unico else st.file_uploader("Arquivo Baixas", type=["xlsx"], key="extra")

xls_base = ler_arquivo(arquivo_base)
xls_extra = ler_arquivo(arquivo_extra)

if xls_base:
    with st.expander("2. Seleção de Abas e Pré-visualização", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            aba_titulos = st.selectbox("Aba Títulos", xls_base.sheet_names)
            df_tit = xls_base.parse(aba_titulos)
            st.dataframe(df_tit.head())

        with col2:
            aba_baixas = st.selectbox("Aba Baixas", xls_extra.sheet_names if xls_extra else [a for a in xls_base.sheet_names if a != aba_titulos])
            df_baix = (xls_extra or xls_base).parse(aba_baixas)
            st.dataframe(df_baix.head())

    # Processamento
    if st.button("🔄 Processar Conciliação"):
        with st.spinner("Calculando conciliação..."):
            colunas = {
                'valor_tit': st.selectbox("Valor Títulos", df_tit.columns),
                'valor_baix': st.selectbox("Valor Baixas", df_baix.columns)
            }
            df_tit['Documento'] = df_tit[st.selectbox("Documento Títulos", df_tit.columns)].astype(str)
            df_baix['Documento'] = df_baix[st.selectbox("Documento Baixas", df_baix.columns)].astype(str)

            df_conc = processar_conciliacao(df_tit, df_baix, colunas)

            st.dataframe(df_conc)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_conc.to_excel(writer, index=False)

            st.download_button("📥 Baixar Conciliação", output.getvalue(), "conciliacao.xlsx")
