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

st.markdown("""
    <style>
        * {
            font-size: 11px !important;
        }
        .stSelectbox > div, .stTextInput > div, .stDataFrame * {
            font-size: 11px !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- ARQUIVOS ---
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

def ler_abas(arquivo):
    if arquivo:
        xls = pd.ExcelFile(arquivo)
        return xls.sheet_names, xls
    return [], None

abas_base, xls_base = ler_abas(arquivo_base)
abas_extra, xls_extra = ler_abas(arquivo_extra)

if xls_base:
    with st.expander("2. Seleção de Abas e Pré-visualização", expanded=True):
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
		usar_extracao_baix = st.checkbox("Extrair Documento e Fornecedor de campo combinado? (Baixas)", key="extrair_baix")
		if usar_extracao_baix:
			campo_combinado_baix = st.selectbox("Campo combinado (Baixas)", df_baix.columns)
			def extrair_info_baixa(texto):
				try:
					doc = re.search(r'NF[:\s]*(\d+)', str(texto)).group(1)
					forn = re.search(r'CLIENTE[:\s]*(.*)', str(texto)).group(1)
					return pd.Series([doc, forn])
				except:
					return pd.Series([None, None])
			df_baix[['Documento', 'Fornecedor']] = df_baix[campo_combinado_baix].apply(extrair_info_baixa)
		else:
			col1_baix, col2_baix = st.columns(2)
			with col1_baix:
				col_doc_baix = st.selectbox("Coluna de Documento - Baixas", df_baix.columns)
				df_baix['Documento'] = df_baix[col_doc_baix]
			with col2_baix:
				col_forn_baix = st.selectbox("Coluna de Fornecedor - Baixas", df_baix.columns)
				df_baix['Fornecedor'] = df_baix[col_forn_baix]

		col1_val, col2_val = st.columns(2)
		with col1_val:
			col_valor_baix = st.selectbox("Coluna de Valor Pago", df_baix.columns)
		with col2_val:
			col_data_baix = st.selectbox("Coluna de Data de Pagamento", df_baix.columns)




    # --- TRATAMENTO ---

    # Conversão de datas e valores
    df_tit[col_data_emissao] = pd.to_datetime(df_tit[col_data_emissao], errors='coerce').dt.strftime('%d/%m/%Y')
    df_tit[col_data_venc] = pd.to_datetime(df_tit[col_data_venc], errors='coerce').dt.strftime('%d/%m/%Y')
    df_baix[col_data_baix] = pd.to_datetime(df_baix[col_data_baix], errors='coerce').dt.strftime('%d/%m/%Y')

    df_tit[col_valor_tit] = pd.to_numeric(df_tit[col_valor_tit], errors='coerce')
    df_baix[col_valor_baix] = pd.to_numeric(df_baix[col_valor_baix], errors='coerce')

    # Garantir colunas para o agrupamento
    df_baix['Documento'] = df_baix[col_doc_baix]
    df_baix['Fornecedor'] = df_baix[col_forn_baix]

    # Agrupando pagamentos
    pagamentos_agrupados = df_baix.groupby(['Documento', 'Fornecedor']).agg({
        col_valor_baix: 'sum'
    }).reset_index().rename(columns={col_valor_baix: 'Valor Pago'})

    # Padronizar tipos para merge
    df_tit['Documento'] = df_tit['Documento'].astype(str)
    df_tit['Fornecedor'] = df_tit['Fornecedor'].astype(str)
    pagamentos_agrupados['Documento'] = pagamentos_agrupados['Documento'].astype(str)
    pagamentos_agrupados['Fornecedor'] = pagamentos_agrupados['Fornecedor'].astype(str)

    # Merge títulos com pagamentos
    df_conc = pd.merge(df_tit, pagamentos_agrupados, on=['Documento', 'Fornecedor'], how='left')
    df_conc['Valor Pago'] = df_conc['Valor Pago'].fillna(0)
    df_conc['Diferença'] = df_conc[col_valor_tit] - df_conc['Valor Pago']
    df_conc['Status Conciliação'] = df_conc['Diferença'].apply(lambda x: 'Liquidado' if abs(x) < 0.01 else 'Pendente')

    # Formatação final
    df_conc[col_valor_tit] = df_conc[col_valor_tit].map("R$ {:,.2f}".format)
    df_conc['Valor Pago'] = df_conc['Valor Pago'].map("R$ {:,.2f}".format)
    df_conc['Diferença'] = df_conc['Diferença'].map("R$ {:,.2f}".format)

    # Exibição final
    st.markdown("## Resultado da Conciliação")
    st.dataframe(df_conc)
