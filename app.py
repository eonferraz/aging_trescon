import streamlit as st
from datetime import datetime
from PIL import Image
from utils.style import aplicar_css
from utils.cabecalho import exibir_cabecalho

# Importar módulos (conforme forem sendo criados)
from modules import upload_dados, conciliacao, resumo  # exemplo

#Chama a função com logo e data
exibir_cabecalho()

#Chama a aplicação de CSS que está em utils
aplicar_css()

# Etapas do processo
st.subheader("1️⃣ Upload dos Arquivos")
upload_dados.executar()  # Exemplo — criaremos esse módulo

st.subheader("2️⃣ Conciliação de Títulos")
conciliacao.executar()  # Próximo passo

st.subheader("3️⃣ Resumo e Exportação")
resumo.executar()
