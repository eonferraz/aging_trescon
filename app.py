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
        /* Melhorias gerais */
        body {
            font-size: 14px !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Melhorar inputs */
        .stTextInput, .stSelectbox, .stSlider, .stFileUploader {
            margin-bottom: 0.5rem;
        }
        
        /* Melhorar tabelas */
        .stDataFrame {
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        
        /* Botões */
        .stButton>button {
            transition: all 0.3s ease;
            border-radius: 6px;
        }
        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Expanders */
        .stExpander .streamlit-expanderHeader {
            font-weight: bold;
            background-color: #f8f9fa;
            border-radius: 8px 8px 0 0;
        }
        
        /* Mensagens de erro */
        .stAlert {
            border-radius: 8px;
        }
        
        /* Cabeçalho */
        .header {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Funções utilitárias
#@st.cache_data
def load_data(uploaded_file):
    """Carrega dados com cache para melhor performance."""
    if uploaded_file is None:
        return None
    try:
        logger.info(f"Lendo arquivo: {uploaded_file.name}")
        return pd.ExcelFile(uploaded_file)
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {str(e)}")
        st.error("Erro ao processar o arquivo. Verifique o formato.")
        return None

def extrair_info(texto):
    """Extrai número de documento e fornecedor do texto.
    
    Args:
        texto (str): Texto contendo as informações
        
    Returns:
        Series: Série com documento e fornecedor
    """
    try:
        doc = re.search(r'NF[:\s]*(\d+)', str(texto)).group(1)
        forn = re.search(r'CLIENTE[:\s]*(.*)', str(texto)).group(1).strip()
        return pd.Series([doc, forn])
    except (AttributeError, TypeError) as e:
        logger.warning(f"Informação não encontrada no texto: {texto}")
        return pd.Series([None, None])

def extrair_forn_similar(texto, fornecedores, cutoff=DEFAULT_CUTOFF):
    """Encontra o fornecedor mais similar na lista.
    
    Args:
        texto (str): Texto para comparar
        fornecedores (list): Lista de fornecedores conhecidos
        cutoff (float): Limite de similaridade (0-1)
        
    Returns:
        str: Nome do fornecedor mais similar ou None
    """
    if not fornecedores or pd.isna(texto):
        return None
        
    try:
        melhores = difflib.get_close_matches(
            str(texto), 
            fornecedores, 
            n=1, 
            cutoff=cutoff
        )
        return melhores[0] if melhores else None
    except Exception as e:
        logger.error(f"Erro ao buscar fornecedor similar: {str(e)}")
        return None

def processar_conciliacao(df_tit, df_baix, colunas):
    """Processa a conciliação entre títulos e baixas.
    
    Args:
        df_tit (DataFrame): DataFrame com os títulos
        df_baix (DataFrame): DataFrame com as baixas
        colunas (dict): Dicionário com os nomes das colunas
        
    Returns:
        DataFrame: DataFrame com o resultado da conciliação
    """
    # Agrupar pagamentos
    pagamentos_agrupados = (
        df_baix.groupby('Documento')[colunas['valor_baix']]
        .sum()
        .reset_index()
        .rename(columns={colunas['valor_baix']: 'Valor Pago'})
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
    df_conc['Diferença'] = df_conc[colunas['valor_tit']] - df_conc['Valor Pago']
    df_conc['Status Conciliação'] = df_conc['Diferença'].apply(
        lambda x: 'Liquidado' if abs(x) < 0.01 else 'Pendente'
    )
    
    # Adicionar informações úteis
    df_conc['% Pago'] = (df_conc['Valor Pago'] / df_conc[colunas['valor_tit']]).round(2)
    
    # Ordenar por status e diferença
    df_conc = df_conc.sort_values(['Status Conciliação', 'Diferença'], ascending=[True, False])
    
    return df_conc

def gerar_relatorio(df_conc, colunas):
    """Gera o relatório em formato Excel.
    
    Args:
        df_conc (DataFrame): DataFrame com dados conciliados
        colunas (dict): Dicionário com os nomes das colunas
        
    Returns:
        BytesIO: Objeto BytesIO com o relatório em Excel
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Aba de conciliação
        df_conc.to_excel(writer, index=False, sheet_name='Conciliação')
        
        # Aba de resumo
        summary = pd.DataFrame({
            'Métrica': ['Total Títulos', 'Total Pago', 'Diferença'],
            'Valor': [
                df_conc[colunas['valor_tit']].sum(),
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
    # Cabeçalho
    st.markdown(
        """
        <div class="header">
            <div style="display: flex; align-items: center; gap: 15px;">
                <img src="https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=304,fit=crop,q=95/Aq2B471lDpFnv1BK/logo---trescon-30-anos-mv0jg6Lo2EiV7yLp.png" style="height: 50px;">
                <div>
                    <h1 style="margin: 0; font-size: 1.8em;">Relatório de Aging - Conciliador</h1>
                    <p style="margin: 0; color: #666;">Versão 1.1 - {date}</p>
                </div>
            </div>
        </div>
        """.format(date=datetime.now().strftime("%d/%m/%Y")),
        unsafe_allow_html=True
    )

    # Seção de ajuda
    with st.expander("❓ Ajuda e Instruções", expanded=False):
        st.markdown("""
        **Guia Rápido:**
        1. Faça upload dos arquivos de títulos e baixas
        2. Selecione as abas corretas em cada arquivo
        3. Defina quais colunas correspondem a cada informação
        4. Clique em "Processar Conciliação"
        
        **Dicas:**
        - Use o mesmo arquivo quando os dados estão em abas diferentes
        - Valores pendentes terão status "Pendente" na conciliação
        - Para melhor performance, evite arquivos muito grandes (>200MB)
        """)

    # Fonte de Dados
    with st.expander("1. Fonte de Dados", expanded=True):
        usar_arquivo_unico = st.checkbox(
            "Usar o mesmo arquivo para Títulos e Baixas",
            help="Marque esta opção se ambos os dados estão no mesmo arquivo em abas diferentes"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            arquivo_base = st.file_uploader(
                "Arquivo Base ou Títulos",
                type=["xlsx", "xls"],
                key="base",
                help="Selecione o arquivo que contém os títulos a pagar"
            )
        with col2:
            arquivo_extra = None if usar_arquivo_unico else st.file_uploader(
                "Arquivo Baixas",
                type=["xlsx", "xls"],
                key="extra",
                help="Selecione o arquivo que contém os pagamentos realizados"
            )

    # Carregar dados
    xls_base = load_data(arquivo_base)
    xls_extra = load_data(arquivo_extra) if not usar_arquivo_unico else xls_base

    if xls_base:
        with st.expander("2. Seleção de Abas e Pré-visualização", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                aba_titulos = st.selectbox(
                    "Aba Títulos",
                    xls_base.sheet_names,
                    help="Selecione a aba que contém os títulos"
                )
                df_tit = xls_base.parse(aba_titulos)
                st.dataframe(df_tit.head(3), height=150)

            with col2:
                aba_baixas = st.selectbox(
                    "Aba Baixas",
                    xls_extra.sheet_names if xls_extra else [a for a in xls_base.sheet_names if a != aba_titulos],
                    help="Selecione a aba que contém os pagamentos realizados"
                )
                df_baix = (xls_extra or xls_base).parse(aba_baixas)
                st.dataframe(df_baix.head(3), height=150)

        # Configuração das colunas
        with st.expander("3. Configuração das Colunas", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                colunas = {
                    'valor_tit': st.selectbox(
                        "Valor Títulos",
                        df_tit.columns,
                        help="Selecione a coluna que contém os valores dos títulos"
                    ),
                    'valor_baix': st.selectbox(
                        "Valor Baixas",
                        df_baix.columns,
                        help="Selecione a coluna que contém os valores dos pagamentos"
                    )
                }
            with col2:
                doc_tit = st.selectbox(
                    "Documento Títulos",
                    df_tit.columns,
                    help="Selecione a coluna que contém o número do documento nos títulos"
                )
                doc_baix = st.selectbox(
                    "Documento Baixas",
                    df_baix.columns,
                    help="Selecione a coluna que contém o número do documento nos pagamentos"
                )

        # Processamento
        if st.button("🔄 Processar Conciliação", type="primary"):
            if not all([colunas['valor_tit'], colunas['valor_baix'], doc_tit, doc_baix]):
                st.error("Por favor, selecione todas as colunas necessárias")
            else:
                with st.spinner("Calculando conciliação..."):
                    try:
                        progress_bar = st.progress(0)
                        
                        # Preparar dados
                        df_tit['Documento'] = df_tit[doc_tit].astype(str)
                        df_baix['Documento'] = df_baix[doc_baix].astype(str)
                        
                        # Converter colunas de valor para número
                        df_tit[colunas['valor_tit']] = pd.to_numeric(df_tit[colunas['valor_tit']], errors='coerce')
                        df_baix[colunas['valor_baix']] = pd.to_numeric(df_baix[colunas['valor_baix']], errors='coerce')

            
                        # Processar conciliação
                        df_conc = processar_conciliacao(df_tit, df_baix, colunas)
                        progress_bar.progress(60)
                        
                        # Exibir resultados
                        st.success("Conciliação concluída com sucesso!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "Total de Títulos", 
                                f"R$ {df_conc[colunas['valor_tit']].sum():,.2f}",
                                help="Soma de todos os títulos a pagar"
                            )
                        with col2:
                            st.metric(
                                "Total Conciliado", 
                                f"R$ {df_conc['Valor Pago'].sum():,.2f}",
                                help="Soma de todos os valores pagos"
                            )
                        with col3:
                            st.metric(
                                "Diferença Total", 
                                f"R$ {df_conc['Diferença'].sum():,.2f}",
                                help="Diferença entre títulos e pagamentos"
                            )
                        
                        progress_bar.progress(80)
                        
                        # Filtros interativos
                        st.subheader("Resultados da Conciliação")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            status_filter = st.multiselect(
                                "Filtrar por Status",
                                options=df_conc['Status Conciliação'].unique(),
                                default=df_conc['Status Conciliação'].unique(),
                                help="Filtre os resultados por status de conciliação"
                            )
                        with col2:
                            min_diff = st.number_input(
                                "Diferença mínima (R$)",
                                min_value=0.0,
                                value=0.0,
                                step=0.01,
                                help="Filtre por valores com diferença maior que"
                            )
                        
                        df_filtered = df_conc[
                            (df_conc['Status Conciliação'].isin(status_filter)) &
                            (df_conc['Diferença'].abs() >= min_diff)
                        ]
                        
                        # Exibir tabela
                        st.dataframe(
                            df_filtered,
                            height=400,
                            use_container_width=True
                        )
                        
                        # Gráficos
                        st.subheader("Visualizações")
                        
                        tab1, tab2 = st.tabs(["Status", "Diferença"])
                        
                        with tab1:
                            st.bar_chart(df_filtered['Status Conciliação'].value_counts())
                        
                        with tab2:
                            st.bar_chart(df_filtered['Diferença'])
                        
                        progress_bar.progress(90)
                        
                        # Exportação
                        st.subheader("Exportar Relatório")
                        output = gerar_relatorio(df_conc, colunas)
                        
                        st.download_button(
                            "📥 Baixar Relatório Completo", 
                            output.getvalue(), 
                            f"conciliacao_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            help="Baixe o relatório completo em Excel com múltiplas abas"
                        )
                        
                        progress_bar.progress(100)
                        
                    except Exception as e:
                        st.error(f"Erro durante o processamento: {str(e)}")
                        logger.error(f"Erro no processamento: {str(e)}")

if __name__ == "__main__":
    main()
