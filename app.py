import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Carteirinha Digital de Treinamento", page_icon="🎓")

# Ocultar menu e rodapé do Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Exibir logo
try:
    logo = Image.open("logo.webp")  # Certifique-se de que o arquivo está no diretório com esse nome
    st.image(logo, width=200)
except:
    st.warning("Logo não encontrada ou nome inválido. Renomeie para 'logo.png' e coloque na mesma pasta do app.")

st.title("Carteirinha Digital de Treinamento")

st.markdown("""
Preencha **RE** e **Data de Admissão** para ver a carteirinha.  
Formato da data: **DD/MM/AAAA** (ex: 15/03/2022)
""")

# Cache para carregar a planilha
@st.cache_data
def carregar_dados():
    df = pd.read_excel("Treinamentos Normativos.xlsx", sheet_name="BASE", engine="openpyxl")
    df["DATA_ADMISSAO"] = pd.to_datetime(df["DATA_ADMISSAO"], errors='coerce').dt.date
    return df

# Colunas fixas
col_cod = "COD_FUNCIONARIO"
col_adm = "DATA_ADMISSAO"
col_nome = "NOME"
col_cargo = "CARGO"
col_trein = "TREINAMENTO_STATUS_GERAL"
col_depto = "DEPARTAMENTO"
col_unidade = "FILIAL_NOME"
col_trilha = "TRILHA DE TREINAMENTO"

trilhas_desejadas = [
    "TRILHA COMPLIANCE",
    "TRILHA DA MANUTENÇÃO",
    "TRILHA SEGURANÇA DO TRABALHO",
    "TRILHA SGI",
    "TRILHA TI"
]

# Carregar dados
df = carregar_dados()

# Entrada do usuário
re_input = st.text_input("Digite seu RE (apenas números):")
admissao_input = st.text_input("Informe a data de admissão (DD/MM/AAAA):")

if st.button("Consultar"):
    if not re_input or not admissao_input:
        st.error("Preencha RE e data de admissão.")
    else:
        try:
            adm_date = datetime.strptime(admissao_input, "%d/%m/%Y").date()
        except:
            st.error("Formato de data inválido. Use DD/MM/AAAA.")
            st.stop()

        # Filtrar dados
        filtro = df.loc[(df[col_cod].astype(str) == str(re_input)) & (df[col_adm] == adm_date)]
        filtro = filtro.loc[filtro[col_trilha].isin(trilhas_desejadas)]

        if filtro.empty:
            st.warning("Nenhum registro encontrado para os critérios informados.")
        else:
            registro = filtro.iloc[0]
            nome, cargo, depto, unidade = registro[[col_nome, col_cargo, col_depto, col_unidade]].values
            st.success(f"{nome} — {cargo} — {depto} — {unidade}")
            st.write(f"RE: **{re_input}** | Admissão: **{adm_date.strftime('%d/%m/%Y')}**")

            st.subheader("Treinamentos:")
            df_display = filtro[[col_trein]].copy()
            df_display[col_trein] = df_display[col_trein].astype(str)
            st.dataframe(df_display.rename(columns={col_trein: "Treinamento"}))
