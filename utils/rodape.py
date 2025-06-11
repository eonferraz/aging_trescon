import streamlit as st
from datetime import datetime
from utils.config import VERSAO_APP, EMPRESA

def exibir_rodape():
    data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    st.markdown(
        f"""
        <hr style="margin-top: 10px; margin-bottom: 5px;">
        <div style="text-align: center; font-size: 0.5em; color: #999;">
            Sistema desenvolvido por Paulo Ferraz para <strong>{EMPRESA}</strong> — Versão {VERSAO_APP}<br>
            Última execução: {data_hora}
        </div>
        """,
        unsafe_allow_html=True
    )
