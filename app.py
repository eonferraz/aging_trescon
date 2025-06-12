#  ______ _________________  ___   ______
#  |  ___|  ___| ___ \ ___ \/ _ \ |___  /
#  | |_  | |__ | |_/ / |_/ / /_\ \   / / 
#  |  _| |  __||    /|    /|  _  |  / /  
#  | |   | |___| |\ \| |\ \| | | |./ /___
#  \_|   \____/\_| \_\_| \_\_| |_/\_____/

#Importação
from utils.config import configurar_pagina

from datetime import datetime
from PIL import Image

from utils.style import aplicar_css
from utils.cabecalho import exibir_cabecalho
from utils.rodape import exibir_rodape
from utils.menu_etapas import exibir_menu_lateral


#Importação dos modulos
from modules import (
    fluxo_importacao_titulos,
    fluxo_extracao_titulos,
    fluxo_importacao_baixas,
    fluxo_extracao_baixas,
    fluxo_conciliacao,
    fluxo_exportacao
)





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


# MENU LATERAL
#=======================================================================================================================================
# Chama o menu lateral
exibir_menu_lateral()

# Fluxo por etapa
if st.session_state["etapa"] == "importacao_titulos":
    fluxo_importacao_titulos.executar()
elif st.session_state["etapa"] == "extracao_titulos":
    fluxo_extracao_titulos.executar()
elif st.session_state["etapa"] == "importacao_baixas":
    fluxo_importacao_baixas.executar()
elif st.session_state["etapa"] == "extracao_baixas":
    fluxo_extracao_baixas.executar()
elif st.session_state["etapa"] == "conciliacao":
    fluxo_conciliacao.executar()
elif st.session_state["etapa"] == "exportacao":
    fluxo_exportacao.executar()

#=======================================================================================================================================





# EXECUÇÃO
#=======================================================================================================================================


# 01. Importação da planilha de títulos
fluxo_extracao_titulos.executar()


#=======================================================================================================================================









#Chama o rodapé
exibir_rodape()
