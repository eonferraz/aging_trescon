import streamlit as st
import pandas as pd
from io import BytesIO
import numpy as np
from rapidfuzz import fuzz
import unidecode

st.set_page_config(layout="wide")

#------------------------------------------------------------------------------------------------------------------------------------------------------
# Logo + título lado a lado
st.markdown(
    """
    <div style="background-color: white; padding: 20px 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center; gap: 20px;">
            <img src="https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=304,fit=crop,q=95/Aq2B471lDpFnv1BK/logo---trescon-30-anos-mv0jg6Lo2EiV7yLp.png" style="height: 60px;">
            <h1 style="margin: 0; font-size: 2.4em;">Aging - Trescon</h1>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

#------------------------------------------------------------------------------------------------------------------------------------------------------

def sugerir_coluna(df, tipo):
    nomes = [col.lower() for col in df.columns]
    sugestoes = {
        'valor': ['valor', 'vlr_total', 'vlr', 'total'],
        'data': ['data', 'dt_pagamento', 'dt_baixa', 'dt_lancamento'],
        'documento': ['documento', 'doc', 'nf', 'nota', 'numero'],
        'parceiro': ['parceiro', 'cliente', 'fornecedor', 'cnpj', 'razao']
    }
    for sugestao in sugestoes[tipo]:
        for i, nome in enumerate(nomes):
            if sugestao in nome:
                return df.columns[i]
    return None

def normalizar_nome(nome):
    return unidecode.unidecode(str(nome)).lower().replace('.', '').replace(' ', '')

# Upload único ou duplo
modo_input = st.radio("Modo de Upload:", ["Arquivo único (com duas abas)", "Dois arquivos separados"], horizontal=True)

df_fin, df_con = None, None

if modo_input == "Arquivo único (com duas abas)":
    arquivo_unico = st.file_uploader("Selecione o arquivo contendo as abas 'Financeiro' e 'Contábil'", type="xlsx")
    if arquivo_unico:
        xls = pd.ExcelFile(arquivo_unico)
        abas = xls.sheet_names
        if "Financeiro" in abas and "Contábil" in abas:
            df_fin = pd.read_excel(xls, sheet_name="Financeiro")
            df_con = pd.read_excel(xls, sheet_name="Contábil")
        else:
            st.warning("As abas 'Financeiro' e 'Contábil' não foram encontradas no arquivo.")
else:
    col1, col2 = st.columns(2)
    with col1:
        arquivo_fin = st.file_uploader("📁 Arquivo Financeiro", type="xlsx", key="fin")
    with col2:
        arquivo_con = st.file_uploader("📁 Arquivo Contábil", type="xlsx", key="con")
    if arquivo_fin and arquivo_con:
        df_fin = pd.read_excel(arquivo_fin)
        df_con = pd.read_excel(arquivo_con)

if df_fin is not None and df_con is not None:
    st.markdown("<style>div[data-testid='stSelectbox'] label, div[data-testid='stRadio'] label, div[data-testid='stTextInput'] label { font-size: 0.85rem !important; }</style>", unsafe_allow_html=True)

    with st.expander("⚙️ Parâmetros de Conciliação", expanded=True):
        col5, col6 = st.columns(2)

        with col5:
            st.write("**Financeiro**")
            st.dataframe(df_fin.head(5), height=150)
            colunas_fin = df_fin.columns.tolist()
            campo_valor_fin = st.selectbox("Campo de Valor:", colunas_fin, index=colunas_fin.index(sugerir_coluna(df_fin, 'valor')) if sugerir_coluna(df_fin, 'valor') in colunas_fin else 0, key="valor_fin")
            df_fin["VALOR_CONSOLIDADO"] = pd.to_numeric(df_fin[campo_valor_fin], errors='coerce')
            campo_data_fin = st.selectbox("Campo de Data:", colunas_fin, index=colunas_fin.index(sugerir_coluna(df_fin, 'data')) if sugerir_coluna(df_fin, 'data') in colunas_fin else 0, key="data_fin")
            df_fin[campo_data_fin] = pd.to_datetime(df_fin[campo_data_fin], errors='coerce')
            campo_doc_fin = st.selectbox("Campo de Documento:", colunas_fin, index=colunas_fin.index(sugerir_coluna(df_fin, 'documento')) if sugerir_coluna(df_fin, 'documento') in colunas_fin else 0, key="doc_fin")
            campo_parceiro_fin = st.selectbox("Campo de Parceiro:", colunas_fin, index=colunas_fin.index(sugerir_coluna(df_fin, 'parceiro')) if sugerir_coluna(df_fin, 'parceiro') in colunas_fin else 0, key="parceiro_fin")

        with col6:
            st.write("**Contábil**")
            st.dataframe(df_con.head(5), height=150)
            colunas_con = df_con.columns.tolist()
            campo_valor_con = st.selectbox("Campo de Valor:", colunas_con, index=colunas_con.index(sugerir_coluna(df_con, 'valor')) if sugerir_coluna(df_con, 'valor') in colunas_con else 0, key="valor_con")
            df_con["VALOR_CONSOLIDADO"] = pd.to_numeric(df_con[campo_valor_con], errors='coerce')
            campo_data_con = st.selectbox("Campo de Data:", colunas_con, index=colunas_con.index(sugerir_coluna(df_con, 'data')) if sugerir_coluna(df_con, 'data') in colunas_con else 0, key="data_con")
            df_con[campo_data_con] = pd.to_datetime(df_con[campo_data_con], errors='coerce')
            campo_doc_con = st.selectbox("Campo de Documento:", colunas_con, index=colunas_con.index(sugerir_coluna(df_con, 'documento')) if sugerir_coluna(df_con, 'documento') in colunas_con else 0, key="doc_con")
            campo_parceiro_con = st.selectbox("Campo de Parceiro:", colunas_con, index=colunas_con.index(sugerir_coluna(df_con, 'parceiro')) if sugerir_coluna(df_con, 'parceiro') in colunas_con else 0, key="parceiro_con")

    if st.button("🔍 Executar Conciliação"):
        with st.spinner("Conciliando registros..."):
            df_fin['STATUS'] = 'Não Encontrado'
            df_fin['PARCEIRO_NORMALIZADO'] = df_fin[campo_parceiro_fin].apply(normalizar_nome)
            df_con['PARCEIRO_NORMALIZADO'] = df_con[campo_parceiro_con].apply(normalizar_nome)

            for i, row_fin in df_fin.iterrows():
                for j, row_con in df_con.iterrows():
                    if abs(row_fin['VALOR_CONSOLIDADO'] - row_con['VALOR_CONSOLIDADO']) <= 0.05:
                        if str(row_fin[campo_doc_fin]).strip() == str(row_con[campo_doc_con]).strip():
                            df_fin.at[i, 'STATUS'] = 'Conciliado'
                            break
                        elif fuzz.partial_ratio(row_fin['PARCEIRO_NORMALIZADO'], row_con['PARCEIRO_NORMALIZADO']) >= 85:
                            df_fin.at[i, 'STATUS'] = 'Parcial'

            resumo = pd.DataFrame({
                'Fonte': ['Financeiro'],
                'Total de Linhas': [len(df_fin)],
                'Conciliados': [len(df_fin[df_fin['STATUS'] == 'Conciliado'])],
                'Parciais': [len(df_fin[df_fin['STATUS'] == 'Parcial'])],
                'Não Encontrados': [len(df_fin[df_fin['STATUS'] == 'Não Encontrado'])]
            })

            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_fin.to_excel(writer, sheet_name='Financeiro', index=False)
                df_con.to_excel(writer, sheet_name='Contabil', index=False)
                resumo.to_excel(writer, sheet_name='Resumo', index=False)

            st.download_button(
                label="📅 Baixar Conciliação em Excel",
                data=buffer.getvalue(),
                file_name="conciliacao_resultado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
