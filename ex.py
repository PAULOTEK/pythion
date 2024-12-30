#!/usr/bin/env python

import requests

# URL e autenticação
URL = 'https://siem.muevy.com/_cat/allocation?v=true'
AUTH = ('aesadmin', 'gjqC@0n46n6>')  # Nome de usuário e senha
TIMEOUT = 10  # Timeout de requisição em segundos


def fetch_allocation_data(url, auth):
    """Faz uma requisição GET para obter os dados de alocação."""
    try:
        response = requests.get(url, auth=auth, timeout=TIMEOUT)
        response.raise_for_status()  # Lança uma exceção para códigos de erro HTTP
        return response
    except requests.exceptions.RequestException as e:
        print(f"Erro ao se conectar: {e}")
        return None


def parse_allocation_data(data):
    """Analisa os dados da resposta e exibe informações detalhadas."""
    lines = data.splitlines()
    if len(lines) <= 1:
        print("Nenhum dado relevante encontrado na resposta.")
        return

    # Separar cabeçalho e dados
    header = lines[0]
    rows = lines[1:]

    # Determina os índices das colunas a partir do cabeçalho
    header_columns = header.split()
    indices = {col: header_columns.index(col) for col in header_columns}

    print("\n--- Informações de Alocação ---\n")

    total_shards = 0
    total_disk_used = 0
    total_disk_total = 0
    total_disk_avail = 0
    unassigned_shards = 0

    # Exibir os dados detalhados para cada linha
    for row in rows:
        columns = row.split()

        # Tratar linha UNASSIGNED (menos colunas do que o cabeçalho)
        if "UNASSIGNED" in row:
            unassigned_shards += int(columns[0])  # Pega o número de shards
            print(f"Shards não atribuídos: {columns[0]}")
            continue

        # Recuperar dados das colunas relevantes
        shards = int(columns[indices['shards']])
        disk_used = parse_disk_size(columns[indices['disk.used']])
        disk_total = parse_disk_size(columns[indices['disk.total']])
        disk_avail = parse_disk_size(columns[indices['disk.avail']])
        disk_percent = columns[indices['disk.percent']] + "%"
        host = columns[indices['host']]
        ip = columns[indices['ip']]
        node = columns[indices['node']]

        total_shards += shards
        total_disk_used += disk_used
        total_disk_total += disk_total
        total_disk_avail += disk_avail

        # Exibir os dados
        print(f"Host: {host}")
        print(f"IP: {ip}")
        print(f"Nó: {node}")
        print(f"Shards: {shards}")
        print(f"Disco usado: {disk_used:.2f} GB")
        print(f"Disco total: {disk_total:.2f} GB")
        print(f"Disco disponível: {disk_avail:.2f} GB")
        print(f"Percentual de uso: {disk_percent}")
        print("-" * 40)

    # Exibir os totais
    print("\n--- Totais ---")
    print(f"Shards totais: {total_shards}")
    print(f"Shards não atribuídos: {unassigned_shards}")
    print(f"Disco usado total: {total_disk_used:.2f} GB")
    print(f"Disco total: {total_disk_total:.2f} GB")
    print(f"Disco disponível total: {total_disk_avail:.2f} GB")
    print("-" * 40)


def parse_disk_size(size_str):
    """Converte tamanhos de disco de string (com sufixos) para GB."""
    if not size_str or size_str == '-':
        return 0  # Para valores vazios ou inexistentes
    size = float(size_str[:-2])  # Remove os últimos dois caracteres (ex: "gb", "tb")
    unit = size_str[-2:].lower()  # Obtém o sufixo (ex: "gb", "tb")

    unit_multipliers = {
        'kb': 1 / (1024 ** 2),  # KB para GB
        'mb': 1 / 1024,  # MB para GB
        'gb': 1,  # GB para GB
        'tb': 1024  # TB para GB
    }

    return size * unit_multipliers.get(unit, 1)


def main():
    response = fetch_allocation_data(URL, AUTH)
    if response:
        print(f"Status da requisição: {response.status_code}")
        parse_allocation_data(response.text)


if __name__ == "__main__":
    main()
 