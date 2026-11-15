import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
BRONZE_DIR = BASE_DIR / 'data' / 'bronze'
INDICADOR_DIR = BASE_DIR / 'data' / 'source'

def ler_dados(nome: str, caminho: Path) -> pd.DataFrame:
    df = pd.read_json(caminho, encoding='utf-8') 

    print(f'=== {nome.upper()} ===')
    print(df.head())
    print(f'[{nome.upper()}] - {df.shape[0]} registros | {df.shape[1]} colunas')
    print(df.dtypes)
    print('Valores nulos:\n', df.isnull().sum())
    print('Linhas duplicadas:', df.duplicated().sum())
    print('Datas duplicadas:', df.duplicated(subset=['data']).sum())

    return df
    
def tratar_dados(nome: str, df: pd.DataFrame) -> pd.DataFrame:
    try:
        if df.empty:
            raise ValueError('Arquivo nao existe')
        
        df = df.copy()
        
        colunas_obrigatorias = ['data', 'valor']
        if not all(coluna in df.columns for coluna in colunas_obrigatorias):
            raise ValueError(f'Coluna obrigatoria ausente em {nome}')

        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        
        df = df.drop_duplicates()

        if df['data'].duplicated().any():
            raise ValueError(f'Existem datas duplicadas em {nome}')

        if df['data'].isnull().any():
            raise ValueError(f'Datas invalidas encontradas em {nome}')

        if df['valor'].isnull().any():
            raise ValueError(f'Valores invalidos encontrados em {nome}')
        
        df['indicador'] = nome
        
        return df

    except Exception as e:
        print(f'Erro, dados invalidos para tratamento: {e}')
        raise
    
def juntar_dados(nome, df, indicador) -> pd.DataFrame:
    if indicador.empty:
        raise ValueError('Arquivo esta vazio')
    
    colunas_obrigatorias = ['indicador', 'categoria', 'unidade']
    if not all(coluna in indicador.columns for coluna in colunas_obrigatorias):
        raise ValueError('Coluna obrigatoria ausente')
    
    if indicador.duplicated(subset=['indicador']).any():
        raise ValueError(f'Dados duplicados em {indicador}')
    
    if indicador.isnull().any().any():
        raise ValueError(f'Valores nulos em {indicador}')
    
    dados_juntos = pd.merge(df, indicador, how='left', on='indicador', validate='many_to_one')
    
    print(f'[{nome.upper()}] - Dados originais - {df.shape[0]} registros | {df.shape[1]} colunas')
    print(f'[{nome.upper()}] - Dados transformados - {dados_juntos.shape[0]} registros | {dados_juntos.shape[1]} colunas')
    
    if not df.shape[0] == dados_juntos.shape[0]:
        raise ValueError(f'Quantidade de linhas nao foi mantida: {df.shape[0]} | {dados_juntos.shape[0]}')
    
    if dados_juntos['categoria'].isnull().any() or dados_juntos['unidade'].isnull().any():
        raise ValueError(f'Existe registros sem dados em {nome}')

    return dados_juntos

def salvar_dados():
    pass
    
arquivos = {
    'selic': 'selic_20261112.json',
    'ipca': 'ipca_20261112.json'
}

dfs = {
    nome: ler_dados(nome, BRONZE_DIR / nome / arquivo)
    for nome, arquivo in arquivos.items()    
}

dfs_silver = {
    nome: tratar_dados(nome, df)
    for nome, df in dfs.items()
}

indicador = pd.read_csv(INDICADOR_DIR / 'indicadores_complementares.csv', encoding='utf-8')

dfs_merge = {
    nome: juntar_dados(nome, df, indicador)
    for nome, df in dfs_silver.items()
}