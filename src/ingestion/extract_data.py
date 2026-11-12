from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
from pathlib import Path
import requests

BASE_URL = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados'
BASE_DIR = Path(__file__).resolve().parents[2]
BRONZE_ROOT = BASE_DIR / 'data' / 'bronze'
BRONZE_ROOT.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "BrazilEconomicDataPipeline/1.0"
}

SERIES = {'selic': 432, 'ipca': 433}

def extract_data(nome_serie: str, codigo: int, anos: int = 10) -> list | None:
    if anos <= 0:
        raise ValueError('O ano precisa ser positivo.')

    hoje = datetime.now()
    data_inicio = hoje - relativedelta(years=anos)

    url = BASE_URL.format(codigo=codigo)
    
    params = {
        'formato': 'json',
        'dataInicial': data_inicio.strftime('%d/%m/%Y'),
        'dataFinal': hoje.strftime('%d/%m/%Y'),
    }

    try:
        response = requests.get(
            url, 
            headers=HEADERS, 
            params=params, 
            timeout=30
        )
        
        response.raise_for_status()
        
        dados = response.json()
        
        if not dados:
            raise ValueError(f'A API nao retornou registros para {nome_serie}')
        
        pasta_destino = BRONZE_ROOT / nome_serie
        pasta_destino.mkdir(parents=True, exist_ok=True)

        caminho_arquivo = pasta_destino / f'{nome_serie}_{hoje.strftime('%Y%m%d')}.json'
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as json_file:
            json.dump(
                dados, 
                json_file, 
                ensure_ascii=False, 
                indent=4
            )
        print(f'[{nome_serie.upper()}] Total: {len(dados)} registros')
        print(f'[{nome_serie.upper()}] Salvo com sucesso em: {caminho_arquivo}')
        
        return dados
    
    except requests.exceptions.RequestException as e:
        print(f'Erro na requisicao ({nome_serie}): {e}')
    except ValueError as e:
        print(f'Erro nos dados ({nome_serie}): {e}')

    return None

for nome, codigo in SERIES.items():
    json_f = extract_data(nome, codigo)