import streamlit as st
import pandas as pd
import sqlite3
import time
from urllib.parse import urlparse

## ---------------------------------------------------------------
# PARTE 2:
# O Dashboard (Transformação -> Disponibilização)
## ---------------------------------------------------------------

# Configuração da página (streamlit)
st.set_page_config(page_title="Personal Downdetector", layout="wide")
st.title("My Personal Downdetector 📉")

# Função para ler dados
def ler_dados():
    conn = sqlite3.connect('meu_monitor.db')
    # Etapa 4: Transformação (SQL Query para pegar os últimos dados)
    query = "SELECT * FROM logs ORDER BY data_hora DESC"
    df = pd.read_sql(query, conn)
    conn.close()

    df['data_hora'] = pd.to_datetime(df['data_hora'])
    return df

# Botão de atualização
if st.button('Update Data'):
    st.rerun()

df = ler_dados()

if not df.empty:
    # Dataframe somente para exibição. 
    # Máscara simples na variável.
    df_display = df.rename(columns={
                           "data_hora": "Date Time",
                           "tempo_resposta": "Response Time (ms)"
                           })
    
    # KPI: status atual (Pega o registro mais recente de cada site)
    st.subheader("Real-Time Status")
    latest_df = df.drop_duplicates(subset=['url'], keep='first')

    # Cria 6 colunas (uma para cada site da lista [SITES] em pipeline.py) 
    colunas = st.columns(len(latest_df))

    # Técnica de escalabilidade para o dashboard, tornando manutenção do pipeline mais fácil
    for i, row in enumerate(latest_df.itertuples()):
        ## ETAPA DE TRANSFORMAÇÃO 
        # 1. Extrai apenas o domínio (ex: www.google.com ou gemini.google.com)
        dominio = urlparse(row.url).netloc

        # 2. Caso o domínio comece com 'www.', fiz esta lógica para remover (interface mais limpa)
        if dominio.startswith("www."):
            site_nome = dominio.replace("www.", "")
        else:
            site_nome = dominio


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

    st.subheader("Latency History")
    
    # Cria uma lista única dos sites disponíveis no banco
    sites_disponiveis = df['url'].unique()
    
    # Cria o componente de seleção múltipla
    sites_selecionados = st.multiselect(
        "Select the websites to view:", 
        options=sites_disponiveis,
        default=sites_disponiveis # Começa com todos marcados
    )
    
    # Filtra o DataFrame baseado na seleção do usuário
    # Se a lista estiver vazia (usuário desmarcou tudo), não mostra nada
    if sites_selecionados:
        df_filtrado = df_display[df_display['url'].isin(sites_selecionados)]
        
        st.line_chart(
            df_filtrado, 
            x="Date Time", 
            y="Response Time (ms)", 
            color="url",
            height=600  
        )
        
        st.subheader("Raw Data")
        st.dataframe(df_filtrado)
    else:
        st.info("Select at least one website above to see the graph.")

else:
    st.warning("No data found. Run pipeline.py first.")


## DISCLAIMER: Coloquei a interface do streamlit em inglês para maior acessibilidade