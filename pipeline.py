import sqlite3 
import requests
import time 
from datetime import datetime

## -----------------------------------------------------------------------
# PARTE 1: 
# O Pipeline (Coleta -> Ingestão -> Armazenamento) 
## -----------------------------------------------------------------------

# Configuração (Lista de URLs)
SITES = [
    "https://ea.uniceub.br/",
    "https://github.com/",
    "https://www.reddit.com/",
    "https://gemini.google.com/",
    "https://www.hackthebox.com/",
    "https://academy.hackthebox.com/"
    # ...
    # Seção para adicionar sites personalizados !
]

# Criando a tabela no banco de dados
def criar_tabela():
    """Preparação do armazenamento"""
    conn = sqlite3.connect('meu_monitor.db')    
    cursor = conn.cursor()
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT,
                        status_code INTEGER,
                        tempo_resposta REAL,
                        data_hora TEXT
                   )
                   ''')
    conn.commit()
    conn.close()


def coletar_dados():
    """Etapa 1: Coleta (collect) e Etapa 4: Transformação simples (transformation)"""
    dados_para_ingestao = []

    # loop simples para automatizar a coleta
    for site in SITES:
        try:
            inicio = time.time()
            resposta = requests.get(site, timeout=7)    
            fim = time.time()

            tempo_ms = round((fim - inicio) * 1000, 2) # Cálculo para transformar seg em ms
            status = resposta.status_code
    # Lógica simples de loop em uma GET request para verificar se o site está "up" ou "down"

        except Exception as e:
            # Site caiu ou atualmente sem internet 
            tempo_ms = 0
            status = 0 # Erro de conexão

        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S") 
        dados_para_ingestao.append((site, status, tempo_ms, timestamp))
        print(f"Coletado: {site} | Status: {status}") # Print para depuração 
            
    return dados_para_ingestao

# Salvando valores no banco de dados
def salvar_no_banco(dados):
    """Etapa 2: Ingestão (ingestion) e Etapa 3: Armazenamento (storage)"""
    conn = sqlite3.connect('meu_monitor.db')
    cursor = conn.cursor()
    cursor.executemany('''
                        INSERT INTO logs (url, status_code, tempo_resposta, data_hora) 
                       VALUES (?, ?, ?, ?)
                        ''', dados) # Atribuindo valores
    conn.commit()
    conn.close()

# Função main que inicia o funcionamento do Pipeline
if __name__ == "__main__":
    criar_tabela()
    print("Iniciando pipeline de monitoramento (CTRL+C para parar)...")
    while True:
        dados = coletar_dados()
        salvar_no_banco(dados)
        time.sleep(60) # Roda a cada 60 segundos (pode-se alterar para melhor experiência)
