from pathlib import Path
import pandas as pd
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[2]
caminho_arquivo = BASE_DIR / 'data' / 'source' / 'indicadores_complementares.csv'

pasta_bronze = BASE_DIR / 'data' / 'bronze' / 'indicadores_complementares'
pasta_bronze.mkdir(parents=True, exist_ok=True)

try:
    df = pd.read_csv(caminho_arquivo, encoding='utf-8')
    
    if df.empty:
        raise ValueError('O arquivo CSV de origem esta vazio.')
    
    colunas_obrigatorias = ['indicador', 'categoria', 'unidade']
    if not all(coluna in df.columns for coluna in colunas_obrigatorias):
        raise ValueError('O CSV nao possui todas as colunas obrigatorias')
        
    print(df.head())
    print(f'Dimensoes: {df.shape}')
    df.info()

    data_execucao = datetime.now().strftime('%Y%m%d')
    nome_arquivo = f'indicadores_complementares_{data_execucao}.csv'
    
    caminho_destino = pasta_bronze / nome_arquivo
    df.to_csv(
        caminho_destino,
        index=False,
        encoding='utf-8'
    )
    
    print(f'Arquivo salvo com sucesso em: {caminho_destino}')

except FileNotFoundError as e:
    print(f'Erro: Arquivo nao encontrado em {caminho_arquivo}')
except Exception as e:
    print(f'Erro inesperado na ingestao: {e}')