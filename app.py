#Importação
from utils.config import configurar_pagina
from datetime import datetime
from PIL import Image
from utils.style import aplicar_css
from utils.cabecalho import exibir_cabecalho
from utils.rodape import exibir_rodape
from modules import importar_titulos
import streamlit as st

# ESTILIZAÇÃO
#=======================================================================================================================================

#Chama a função para configurar a página
configurar_pagina()  # deve ser o primeiro comando antes de qualquer uso do Streamlit

#Chama a função com logo e data
exibir_cabecalho()

#Chama a aplicação de CSS que está em utils
aplicar_css()

#=======================================================================================================================================

# EXECUÇÃO
#=======================================================================================================================================


# 01. Importação da planilha de títulos













#=======================================================================================================================================









#Chama o rodapé

exibir_rodape()
