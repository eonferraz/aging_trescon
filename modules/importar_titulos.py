from modules import extrator_titulos  # novo import

import streamlit as st  # Importa o Streamlit para construção da interface
import pandas as pd     # Importa o pandas para leitura e manipulação de dados

def executar():
    
    # Cria um componente para upload de arquivos Excel (.xlsx)
    arquivo = st.file_uploader("Selecionar arquivo Excel (.xlsx)", type=["xlsx"])

    # Só executa a leitura se o usuário carregar um arquivo
    if arquivo:
        try:
            # Lê todas as abas do arquivo Excel (sem ainda carregar os dados)
            abas = pd.ExcelFile(arquivo).sheet_names

            # Cria um selectbox para o usuário escolher a aba que deseja importar
            aba_selecionada = st.selectbox("Selecione a aba a ser importada", abas)

            # Se uma aba foi selecionada, realiza a leitura da planilha específica
            if aba_selecionada:
                df = pd.read_excel(arquivo, sheet_name=aba_selecionada)

                # Armazena o DataFrame no session_state para uso posterior nos outros módulos
                st.session_state["df_titulos"] = df

                # Exibe uma mensagem de sucesso
                st.success(f"Aba '{aba_selecionada}' carregada com sucesso!")

                # Mostra os dados carregados dentro de um expander
                with st.expander("📋 Visualizar dados importados"):
                    st.dataframe(df, use_container_width=True)
                    
                # 🔁 Etapa opcional: extração de campos a partir de colunas misturadas
                with st.expander("🧠 Extrair Campos do Texto (Histórico, NF, Fornecedor etc.)"):
                    extrator_titulos.executar(df)
       

        # Caso ocorra algum erro na leitura do arquivo ou da aba, exibe mensagem de erro
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
