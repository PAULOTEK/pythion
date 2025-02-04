#!/usr/bin/env python

import requests
import datetime
import argparse
from colorama import Fore, Style, init

# Inicializa colorama para cores no terminal
init(autoreset=True)

# URLs e autenticação padrão
DEFAULT_ALLOCATION_URL = 'https://siem.muevy.com/_cat/allocation?v=true'
DEFAULT_INDICES_URL = 'https://siem.muevy.com/_cat/indices?v=true&h=index,pri,rep,store.size,creation.date,status'
DEFAULT_AUTH = ('aesadmin', 'gjqC@0n46n6>')  # Nome de usuário e senha
TIMEOUT = 10  # Timeout de requisição em segundos


def fetch_elastic_data(url, auth):
    """Faz uma requisição GET para obter dados do Elasticsearch."""
    try:
        response = requests.get(url, auth=auth, timeout=TIMEOUT)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Erro ao se conectar: {e}")
        return None


def parse_allocation_data(data):
    """Analisa os dados de alocação de armazenamento."""
    lines = data.splitlines()
    if len(lines) <= 1:
        print(Fore.YELLOW + "Nenhum dado relevante encontrado na resposta.")
        return

    header = lines[0].split()
    rows = lines[1:]

    # Verifica se as colunas esperadas estão presentes
    required_columns = ['disk.used', 'disk.total', 'disk.avail']
    if not all(col in header for col in required_columns):
        print(Fore.RED + f"Colunas esperadas não encontradas: {required_columns}")
        return

    indices = {col: idx for idx, col in enumerate(header)}
    total_disk_used = 0
    total_disk_total = 0
    total_disk_avail = 0

    print(Fore.CYAN + "\n--- Alocação de Armazenamento ---\n")

    for row in rows:
        if "UNASSIGNED" in row:
            continue

        columns = row.split()
        disk_used = parse_disk_size(columns[indices['disk.used']])
        disk_total = parse_disk_size(columns[indices['disk.total']])
        disk_avail = parse_disk_size(columns[indices['disk.avail']])

        total_disk_used += disk_used
        total_disk_total += disk_total
        total_disk_avail += disk_avail

    print(f"Espaço total usado: {Fore.GREEN}{total_disk_used:.2f} GB")
    print(f"Espaço total disponível: {Fore.GREEN}{total_disk_avail:.2f} GB")
    print(f"Espaço total do cluster: {Fore.GREEN}{total_disk_total:.2f} GB\n")


def parse_indices_data(data, top_n=None):
    """Analisa os dados de índices."""
    lines = data.splitlines()
    if len(lines) <= 1:
        print(Fore.YELLOW + "Nenhum índice encontrado.")
        return

    header = lines[0].split()
    rows = lines[1:]
    col_indices = {col: idx for idx, col in enumerate(header)}

    # Verifica se as colunas esperadas estão presentes
    required_columns = ['index', 'pri', 'rep', 'store.size', 'creation.date', 'status']
    if not all(col in header for col in required_columns):
        print(Fore.RED + f"Colunas esperadas não encontradas: {required_columns}")
        return

    # Usa datetime.UTC para criar objetos timezone-aware
    today = datetime.datetime.now(datetime.UTC).date()
    indices_hoje = 0
    total_size_gb = 0
    indices_info = []

    for row in rows:
        columns = row.split()

        # Ignorar índices fechados
        if columns[col_indices['status']] != 'open':
            continue

        # Processar dados do índice
        index = columns[col_indices['index']]
        pri = int(columns[col_indices['pri']])
        rep = int(columns[col_indices['rep']])
        size_str = columns[col_indices['store.size']]
        creation_date = datetime.datetime.fromtimestamp(
            int(columns[col_indices['creation.date']]) / 1000, tz=datetime.UTC
        ).date()

        # Calcular métricas
        size_gb = parse_disk_size(size_str)
        total_shards = pri * (rep + 1)
        criado_hoje = creation_date == today

        if criado_hoje:
            indices_hoje += 1

        total_size_gb += size_gb
        indices_info.append((index, total_shards, size_gb, criado_hoje))

    # Ordenar por tamanho
    indices_info.sort(key=lambda x: x[2], reverse=True)

    # Limitar ao top N índices, se especificado
    if top_n:
        indices_info = indices_info[:top_n]

    print(Fore.CYAN + "\n--- Estatísticas de Índices ---")
    print(f"Índices criados hoje: {Fore.GREEN}{indices_hoje}")
    print(f"Total de índices abertos: {Fore.GREEN}{len(indices_info)}")
    print(f"Espaço total ocupado por índices: {Fore.GREEN}{total_size_gb:.2f} GB\n")

    print(Fore.CYAN + "Detalhes dos Índices (maiores primeiro):")
    for idx in indices_info:
        print(f"Nome: {Fore.YELLOW}{idx[0]}")
        print(f"Shards: {idx[1]}")
        print(f"Tamanho: {Fore.GREEN}{idx[2]:.2f} GB")
        print(f"Criado hoje: {Fore.GREEN if idx[3] else Fore.RED}{'Sim' if idx[3] else 'Não'}")
        print("-" * 40)


def parse_disk_size(size_str):
    """Converte tamanhos de string para GB."""
    if not size_str or size_str == '-':
        return 0.0

    unit = size_str[-2:].lower()
    value = float(size_str[:-2])

    multipliers = {
        'kb': 1 / 1024 ** 2,
        'mb': 1 / 1024,
        'gb': 1,
        'tb': 1024
    }

    return value * multipliers.get(unit, 1)


def main():
    parser = argparse.ArgumentParser(description="Monitoramento de Elasticsearch")
    parser.add_argument('--allocation-url', default=DEFAULT_ALLOCATION_URL, help="URL para dados de alocação")
    parser.add_argument('--indices-url', default=DEFAULT_INDICES_URL, help="URL para dados de índices")
    parser.add_argument('--username', default=DEFAULT_AUTH[0], help="Usuário para autenticação")
    parser.add_argument('--password', default=DEFAULT_AUTH[1], help="Senha para autenticação")
    parser.add_argument('--top', type=int, help="Número de índices maiores para exibir")
    args = parser.parse_args()

    auth = (args.username, args.password)

    # Obter dados de alocação
    alloc_response = fetch_elastic_data(args.allocation_url, auth)
    if alloc_response:
        parse_allocation_data(alloc_response.text)

    # Obter dados de índices
    indices_response = fetch_elastic_data(args.indices_url, auth)
    if indices_response:
        parse_indices_data(indices_response.text, top_n=args.top)


if __name__ == "__main__":
    main()