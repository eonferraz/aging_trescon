import streamlit as st
from datetime import datetime

# Cabeçalho com logo e data
st.markdown(
    """
    <div class="header">
        <div style="display: flex; align-items: center; gap: 15px;">
            <img src="https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=304,fit=crop,q=95/Aq2B471lDpFnv1BK/logo---trescon-30-anos-mv0jg6Lo2EiV7yLp.png" style="height: 50px;">
            <div>
                <h1 style="margin: 0; font-size: 1.8em;">Relatório de Aging - Conciliador</h1>
                <p style="margin: 0; color: #666;">Versão 1.1 - {date}</p>
            </div>
        </div>
    </div>
    """.format(date=datetime.now().strftime("%d/%m/%Y")),
    unsafe_allow_html=True
)
