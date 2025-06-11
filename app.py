#Importação
from utils.config import configurar_pagina

from datetime import datetime
from PIL import Image

from utils.style import aplicar_css
from utils.cabecalho import exibir_cabecalho
from utils.rodape import exibir_rodape
from modules import fluxo_importacao
from utils.menu_etapas import exibir_menu_lateral

import streamlit as st


# ESTILIZAÇÃO
#=======================================================================================================================================

#Chama a função para configurar a página
configurar_pagina()  # deve ser o primeiro comando antes de qualquer uso do Streamlit

#Chama a função com logo e data
exibir_cabecalho()

#Chama a aplicação de CSS que está em utils
aplicar_css()


# Mostra o menu lateral
exibir_menu_lateral()


#=======================================================================================================================================





# EXECUÇÃO
#=======================================================================================================================================


# 01. Importação da planilha de títulos
st.markdown("<div class='custom-subheader'>1️⃣ Importação dos Títulos</div>", unsafe_allow_html=True)

fluxo_importacao.executar()


#=======================================================================================================================================









#Chama o rodapé
exibir_rodape()
