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
st.markdown("<div class='custom-subheader'>1️⃣ Importação dos Títulos</div>", unsafe_allow_html=True)

fluxo_importacao.executar()


#=======================================================================================================================================









#Chama o rodapé
exibir_rodape()
