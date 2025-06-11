
#Chama a função para configurar a página
from utils.config import configurar_pagina
configurar_pagina()  # deve ser o primeiro comando antes de qualquer uso do Streamlit


import streamlit as st
from datetime import datetime
from PIL import Image
from utils.style import aplicar_css
from utils.cabecalho import exibir_cabecalho

#Chama a função com logo e data
exibir_cabecalho()

#Chama a aplicação de CSS que está em utils
aplicar_css()


#Chama o rodapé
from utils.rodape import exibir_rodape
exibir_rodape()
