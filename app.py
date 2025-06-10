import streamlit as st
import pandas as pd
import io
import re
import difflib
import logging
from datetime import datetime

# Configurações iniciais
st.set_page_config(page_title="Aging - Conciliador", layout="wide", page_icon="📊")

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes
DEFAULT_CUTOFF = 0.4
MAX_UPLOAD_SIZE = 200  # MB

# CSS customizado
st.markdown("""
    <style>
        /* Seu CSS personalizado permanece o mesmo */
    </style>
""", unsafe_allow_html=True)

# Funções utilitárias
@st.cache_data
def load_sheet(uploaded_file, sheet_name=None):
    """Carrega uma aba específica do arquivo Excel com cache."""
    if uploaded_file is None:
        return None
    try:
        if sheet_name:
            return pd.read_excel(uploaded_file, sheet_name=sheet_name)
        return pd.read_excel(uploaded_file)
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {str(e)}")
        st.error("Erro ao processar o arquivo. Verifique o formato.")
        return None

def get_sheet_names(uploaded_file):
    """Obtém os nomes das abas de um arquivo Excel."""
    if uploaded_file is None:
        return []
    try:
        return pd.ExcelFile(uploaded_file).sheet_names
    except Exception as e:
        logger.error(f"Erro ao obter abas do arquivo: {str(e)}")
        return []

def processar_conciliacao(df_tit, df_baix, config):
    """Processa a conciliação entre títulos e baixas."""
    try:
        # Converter colunas numéricas
        df_tit[config['valor_tit']] = pd.to_numeric(df_tit[config['valor_tit']], errors='coerce')
        df_baix[config['valor_baix']] = pd.to_numeric(df_baix[config['valor_baix']], errors='coerce')
        
        # Remover linhas com valores inválidos
        df_tit = df_tit.dropna(subset=[config['valor_tit'], config['doc_tit']])
        df_baix = df_baix.dropna(subset=[config['valor_baix'], config['doc_baix']])
        
        # Garantir que a coluna de documento é string
        df_tit['Documento'] = df_tit[config['doc_tit']].astype(str)
        df_baix['Documento'] = df_baix[config['doc_baix']].astype(str)
        
        # Agrupar pagamentos
        pagamentos_agrupados = (
            df_baix.groupby('Documento')[config['valor_baix']]
            .sum()
            .reset_index()
            .rename(columns={config['valor_baix']: 'Valor Pago'})
        )
        
        # Merge com os títulos
        df_conc = pd.merge(
            df_tit, 
            pagamentos_agrupados, 
            on='Documento', 
            how='left',
            indicator=True
        )
        
        # Tratar valores nulos
        df_conc['Valor Pago'] = df_conc['Valor Pago'].fillna(0)
        
        # Calcular diferença e status
        df_conc['Diferença'] = df_conc[config['valor_tit']] - df_conc['Valor Pago']
        df_conc['Status Conciliação'] = df_conc['Diferença'].apply(
            lambda x: 'Liquidado' if abs(x) < 0.01 else 'Pendente'
        )
        
        # Adicionar informações úteis
        df_conc['% Pago'] = (df_conc['Valor Pago'] / df_conc[config['valor_tit']]).round(2)
        
        # Manter colunas de referência
        colunas_manter = ['Documento', config['valor_tit'], 'Valor Pago', 'Diferença', 
                         'Status Conciliação', '% Pago']
        
        # Adicionar colunas adicionais de referência se especificadas
        if 'forn_tit' in config:
            df_conc['Fornecedor'] = df_tit[config['forn_tit']]
            colunas_manter.append('Fornecedor')
            
        if 'data_tit' in config:
            df_conc['Data Título'] = df_tit[config['data_tit']]
            colunas_manter.append('Data Título')
            
        if 'data_baix' in config:
            # Para múltiplas baixas, pegar a última data
            ultimas_baixas = df_baix.groupby('Documento')[config['data_baix']].max().reset_index()
            df_conc = pd.merge(df_conc, ultimas_baixas, on='Documento', how='left')
            df_conc.rename(columns={config['data_baix']: 'Data Baixa'}, inplace=True)
            colunas_manter.append('Data Baixa')
        
        # Ordenar por status e diferença
        df_conc = df_conc[colunas_manter].sort_values(['Status Conciliação', 'Diferença'], ascending=[True, False])
        
        return df_conc
    
    except Exception as e:
        logger.error(f"Erro no processamento: {str(e)}")
        raise

def gerar_relatorio(df_conc, config):
    """Gera o relatório em formato Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Aba de conciliação
        df_conc.to_excel(writer, index=False, sheet_name='Conciliação')
        
        # Aba de resumo
        summary = pd.DataFrame({
            'Métrica': ['Total Títulos', 'Total Pago', 'Diferença'],
            'Valor': [
                df_conc[config['valor_tit']].sum(),
                df_conc['Valor Pago'].sum(),
                df_conc['Diferença'].sum()
            ]
        })
        summary.to_excel(writer, index=False, sheet_name='Resumo')
        
        # Aba de análise
        analysis = df_conc['Status Conciliação'].value_counts().reset_index()
        analysis.columns = ['Status', 'Quantidade']
        analysis.to_excel(writer, index=False, sheet_name='Análise')
    
    return output

# Interface do usuário
def main():
    """Função principal que renderiza a interface do usuário."""
    # Cabeçalho (mantido igual)
    
    # Seção de ajuda (mantida igual)
    
    # Fonte de Dados (mantida igual)
    
    # Obter nomes das abas
    sheet_names_base = get_sheet_names(arquivo_base)
    sheet_names_extra = get_sheet_names(arquivo_extra) if not usar_arquivo_unico else sheet_names_base

    if arquivo_base:
        with st.expander("2. Seleção de Abas e Pré-visualização", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                aba_titulos = st.selectbox(
                    "Aba Títulos",
                    sheet_names_base,
                    help="Selecione a aba que contém os títulos"
                )
                df_tit = load_sheet(arquivo_base, aba_titulos)
                if df_tit is not None:
                    st.dataframe(df_tit.head(3), height=150)

            with col2:
                aba_baixas = st.selectbox(
                    "Aba Baixas",
                    sheet_names_extra,
                    help="Selecione a aba que contém os pagamentos realizados"
                )
                df_baix = load_sheet(arquivo_extra if not usar_arquivo_unico else arquivo_base, aba_baixas)
                if df_baix is not None:
                    st.dataframe(df_baix.head(3), height=150)

        # Configuração das colunas
        if df_tit is not None and df_baix is not None:
            with st.expander("3. Configuração das Colunas", expanded=True):
                config = {}
                
                st.subheader("Colunas para Títulos")
                col1, col2 = st.columns(2)
                with col1:
                    config['doc_tit'] = st.selectbox(
                        "Documento (Títulos)",
                        df_tit.columns,
                        help="Selecione a coluna que contém o número do documento nos títulos"
                    )
                    config['valor_tit'] = st.selectbox(
                        "Valor (Títulos)",
                        df_tit.columns,
                        help="Selecione a coluna que contém os valores dos títulos"
                    )
                with col2:
                    config['forn_tit'] = st.selectbox(
                        "Fornecedor (Títulos) - Opcional",
                        ['Não utilizar'] + list(df_tit.columns),
                        index=0,
                        help="Selecione a coluna que contém o nome do fornecedor"
                    )
                    config['data_tit'] = st.selectbox(
                        "Data (Títulos) - Opcional",
                        ['Não utilizar'] + list(df_tit.columns),
                        index=0,
                        help="Selecione a coluna que contém a data do título"
                    )
                
                st.subheader("Colunas para Baixas")
                col3, col4 = st.columns(2)
                with col3:
                    config['doc_baix'] = st.selectbox(
                        "Documento (Baixas)",
                        df_baix.columns,
                        help="Selecione a coluna que contém o número do documento nos pagamentos"
                    )
                    config['valor_baix'] = st.selectbox(
                        "Valor (Baixas)",
                        df_baix.columns,
                        help="Selecione a coluna que contém os valores dos pagamentos"
                    )
                with col4:
                    config['data_baix'] = st.selectbox(
                        "Data (Baixas) - Opcional",
                        ['Não utilizar'] + list(df_baix.columns),
                        index=0,
                        help="Selecione a coluna que contém a data do pagamento"
                    )
                
                # Remover campos não utilizados
                if config['forn_tit'] == 'Não utilizar':
                    del config['forn_tit']
                if config['data_tit'] == 'Não utilizar':
                    del config['data_tit']
                if config['data_baix'] == 'Não utilizar':
                    del config['data_baix']

            # Processamento
            if st.button("🔄 Processar Conciliação", type="primary"):
                if not all([config.get('valor_tit'), config.get('valor_baix'), 
                          config.get('doc_tit'), config.get('doc_baix')]):
                    st.error("Por favor, selecione todas as colunas obrigatórias")
                else:
                    with st.spinner("Calculando conciliação..."):
                        try:
                            progress_bar = st.progress(0)
                            
                            # Processar conciliação
                            df_conc = processar_conciliacao(df_tit, df_baix, config)
                            progress_bar.progress(60)
                            
                            # Exibir resultados (mantido igual)
                            
                            # Exportação (mantido igual)
                            
                        except Exception as e:
                            st.error(f"Erro durante o processamento: {str(e)}")
                            logger.error(f"Erro detalhado: {str(e)}")

if __name__ == "__main__":
    main()
