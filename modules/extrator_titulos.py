import streamlit as st
import pandas as pd
import re


def executar(df):
    st.markdown("<div class='custom-subheader'>🧠 Mapeamento e Extração Assistida de Campos</div>", unsafe_allow_html=True)

    if df.empty or df.shape[1] == 0:
        st.warning("Nenhum dado disponível para análise. Importe os títulos primeiro.")
        return

    colunas = df.columns.tolist()
    campos_mapeados = {}
    campos_com_tratamento = {}

    # Layout em duas colunas
    col_esq, col_dir = st.columns([3, 2])

    with col_esq:
        st.markdown("### 🧾 Visualização dos Dados Importados")
        st.dataframe(df.head(10), use_container_width=True)

    with col_dir:
        st.markdown("### 🛠️ Mapeamento de Campos")
        for campo in CAMPOS_LOGICOS:
            st.markdown(f"`{campo}`")
            sel_col, chk = st.columns([2, 1])
            with sel_col:
                coluna_selecionada = st.selectbox(
                    f"Coluna para {campo}",
                    colunas,
                    key=f"sel_col_{campo}"
                )
            with chk:
                precisa_tratar = st.checkbox("Regex?", key=f"chk_regex_{campo}", value=True)

            campos_mapeados[campo] = coluna_selecionada
            campos_com_tratamento[campo] = precisa_tratar

    # Aplicação de extrações ou cópias diretas
    st.markdown("---")
    st.markdown("### ✨ Resultados das Extrações")

    df_resultado = df.copy()

    for campo, coluna in campos_mapeados.items():
        if campos_com_tratamento[campo]:
            regex = REGEX_SUGERIDA.get(campo, "")
            extraido = aplicar_regex_em_coluna(df, coluna, regex)

            if extraido is not None and extraido.notna().sum() > 0:
                df_resultado[campo] = extraido
                st.success(f"Campo '{campo}' extraído com sucesso da coluna '{coluna}'")
                st.dataframe(
                    pd.DataFrame({
                        "Texto Original": df[coluna].head(5),
                        f"{campo} Extraído": extraido.head(5)
                    }),
                    use_container_width=True
                )
            else:
                st.warning(f"Não foi possível extrair '{campo}' da coluna '{coluna}' com a regex padrão.")
        else:
            df_resultado[campo] = df[coluna]
            st.info(f"Campo '{campo}' definido diretamente da coluna '{coluna}' (sem regex).")
            st.dataframe(df[[coluna]].head(5).rename(columns={coluna: campo}), use_container_width=True)

    st.session_state["df_titulos"] = df_resultado
    st.markdown("---")
    st.success("✅ Mapeamento e tratamento concluídos. Dados prontos para conciliação ou exportação.")
