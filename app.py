#  ______ _________________  ___   ______
#  |  ___|  ___| ___ \ ___ \/ _ \ |___  /
#  | |_  | |__ | |_/ / |_/ / /_\ \   / / 
#  |  _| |  __||    /|    /|  _  |  / /  
#  | |   | |___| |\ \| |\ \| | | |./ /___
#  \_|   \____/\_| \_\_| \_\_| |_/\_____/
#

#Importação
from utils.config import configurar_pagina

from datetime import datetime
from PIL import Image

from utils.style import aplicar_css
from utils.cabecalho import exibir_cabecalho
from utils.rodape import exibir_rodape
# from utils.menu_etapas import exibir_menu_lateral

#Importação dos modulos
# from modules import (
#     fluxo_importacao_titulos,
#     fluxo_extracao_titulos,
#     fluxo_importacao_baixas,
#     fluxo_extracao_baixas,
#     fluxo_extracao_conciliado,
#     fluxo_importacao_conciliado,
#     fluxo_conciliacao,
#     fluxo_exportacao
# )

from modules import (
    fluxo_importacao_conciliado,
    fluxo_extracao_conciliado,
    fluxo_importacao_titulos,
    fluxo_extracao_titulos,
    fluxo_unificacao_titulos_conciliado,
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


# ETAPAS EM FORMATO EXPANSÍVEL
#=======================================================================================================================================
with st.expander("1️⃣ Conciliação Anterior", expanded=True):
    fluxo_importacao_conciliado.executar()
    if "df_conciliado_bruto" in st.session_state:
        fluxo_extracao_conciliado.executar(st.session_state["df_conciliado_bruto"])
    else:
        st.warning("Você precisa importar a conciliação anterior primeiro.")

with st.expander("2️⃣ Títulos Novos", expanded=True):
    fluxo_importacao_titulos.executar()
    if "df_titulos" in st.session_state:
        fluxo_extracao_titulos.executar()
    else:
        st.warning("Você precisa importar os títulos antes de extrair.")

with st.expander("3️⃣ Unificar Títulos + Conciliação Anterior", expanded=True):
    if "df_titulos_extraido" in st.session_state and "df_conciliado_extraido" in st.session_state:
        fluxo_unificacao_titulos_conciliado.executar()
    else:
        st.warning("Importe e extraia os títulos e a conciliação anterior antes de unificar.")

with st.expander("4️⃣ Baixas", expanded=True):
    fluxo_importacao_baixas.executar()
    if "df_baixas" in st.session_state:
        fluxo_extracao_baixas.executar()
    else:
        st.warning("Você precisa importar as baixas antes de extrair.")

with st.expander("5️⃣ Conciliação Final", expanded=True):
    if "df_unificado" in st.session_state and "df_baixas_extraido" in st.session_state:
        fluxo_conciliacao.executar()
        fluxo_exportacao.executar()
    else:
        st.warning("A conciliação só pode ser feita após unificar os títulos e extrair as baixas.")
#=======================================================================================================================================

# Rodapé
exibir_rodape()
#=======================================================================================================================================
