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

# Inicializa o estado das etapas concluídas
if "etapas_concluidas" not in st.session_state:
    st.session_state["etapas_concluidas"] = []

# Etapa 1 - Importação Títulos
fluxo_importacao_titulos.executar()

# Etapa 2 - Extração Títulos (se df_titulos estiver presente)
if "df_titulos" in st.session_state:
    fluxo_extracao_titulos.executar()

# Etapa 3 - Importação Baixas
if "extracao_titulos" in st.session_state["etapas_concluidas"]:
    fluxo_importacao_baixas.executar()

# Etapa 4 - Extração Baixas
if "df_baixas" in st.session_state:
    fluxo_extracao_baixas.executar()

# Etapa 5 - Conciliação
if "extracao_baixas" in st.session_state["etapas_concluidas"]:
    fluxo_conciliacao.executar()

# Etapa 6 - Exportação
if "conciliacao" in st.session_state["etapas_concluidas"]:
    fluxo_exportacao.executar()

#=======================================================================================================================================



#Chama o rodapé
exibir_rodape()
