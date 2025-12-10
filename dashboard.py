import streamlit as st
import pandas as pd
import sqlite3
import time

## ---------------------------------------------------------------
# PARTE 2:
# O Dashboard (Transformação -> Disponibilização)
## ---------------------------------------------------------------

# Configuração da página
st.set_page_config(page_title="Personal Downdetector", layout="wide")
st.title("My Personal Downdetector 📉")

# Função para ler dados
def ler_dados():
    conn = sqlite3.connect('meu_monitor.db')
    # Etapa 4: Transformação (SQL Query para pegar os últimos dados)
    query = "SELECT * FROM logs ORDER BY data_hora DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Botão de atualização
if st.button('Atualizar Dados'):
    st.rerun()

df = ler_dados()

if not df.empty:
    # KPI: status atual (Pega o registro mais recente de cada site)
    st.subheader("Status em tempo real")
    latest_df = df.drop_duplicates(subset=['url'], keep='first')

    # Cria 6 colunas (uma para cada site da lista [SITES] em pipeline.py) 
    colunas = st.columns(len(latest_df))

    # Técnica de escalabilidade para o dashboard, tornando manutenção do pipeline mais fácil
    for i, row in enumerate(latest_df.itertuples()):
        ## ETAPA DE TRANSFORMAÇÃO 
        # 1. Tira o https://
        # 2. Tira o www. (se tiver)
        # 3. Tira a barra final / (se tiver)
        site_nome = row.url.replace("https://", "").replace("www", "").replace("/", "")

        status_msg = "UP" if row.status_code == 200 else "DOWN"

        # Define a cor do texto 
        # NOTA: delta_color="normal" (verde) ou "inverse" (vermelho)
        cor_delta = "normal" if row.status_code == 200 else "inverse"

        # Desenha na coluna 'i' correspondente
        colunas[i].metric(
            label=site_nome,
            value=f"{row.tempo_resposta} ms",
            delta=status_msg,
            delta_color=cor_delta
        )

    st.divider()

    # Histórico
    st.subheader("Histórico de latência")
    st.line_chart(df, x="data_hora", y="tempo_resposta", color="url")

    st.subheader("Dados Brutos")
    st.dataframe(df)
else:
    st.warning("Nenhum dado encontrado. Execute o pipeline.py primeiro")