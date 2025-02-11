# #!/usr/bin/env python
#
# import requests
# from collections import defaultdict
#
# # URL e autenticação
# URL = 'https://siem.muevy.com/_cat/allocation?v=true'
# INDEX_URL = 'https://siem.muevy.com/_cat/indices?v=true'
# AUTH = ('aesadmin', 'gjqC@0n46n6>')  # Nome de usuário e senha
# TIMEOUT = 10  # Timeout de requisição em segundos
#
#
# def fetch_data(url, auth):
#     """Faz uma requisição GET para obter os dados."""
#     try:
#         response = requests.get(url, auth=auth, timeout=TIMEOUT)
#         response.raise_for_status()
#         return response.text
#     except requests.exceptions.RequestException as e:
#         print(f"Erro ao se conectar: {e}")
#         return None
#
#
# def parse_disk_size(size_str):
#     """Converte tamanhos de disco de string (com sufixos) e retorna o valor convertido e a unidade original."""
#     if not size_str or size_str == '-':
#         return 0, "0 B"
#     size = float(size_str[:-2])
#     unit = size_str[-2:].lower()
#     unit_multipliers = {'kb': 1 / 1024, 'mb': 1, 'gb': 1024, 'tb': 1024 ** 2}
#     converted_size = size * unit_multipliers.get(unit, 1)
#     return converted_size, f"{size} {unit.upper()}"
#
#
# def format_size(size_mb):
#     """Formata o tamanho para a unidade mais apropriada."""
#     if size_mb >= 1024:
#         return f"{size_mb / 1024:.2f} GB"
#     elif size_mb >= 1:
#         return f"{size_mb:.2f} MB"
#     else:
#         return f"{size_mb * 1024:.2f} KB"
#
#
# def parse_index_data(data):
#     """Exibe informações sobre os índices e soma o total por prefixo e categorias específicas."""
#     lines = data.splitlines()
#     if len(lines) <= 1:
#         print("Nenhum dado relevante encontrado nos índices.")
#         return
#
#     header = lines[0].split()
#     rows = lines[1:]
#     indices = {col: header.index(col) for col in header}
#
#     total_disk_size = 0
#     category_totals = defaultdict(float)
#     specific_totals = {"cwl-": 0, "log-ocsf-identity": 0, "metrics-opensearch-index": 0,
#                        "log-ocsf-findings": 0, "log-ocsf-network": 0, "log-ocsf-application": 0}
#
#     for row in rows:
#         columns = row.split()
#         index_name = columns[indices['index']]
#         converted_size, original_str = parse_disk_size(columns[indices['store.size']])
#         total_disk_size += converted_size
#
#         category = index_name.split('-')[0]
#         category_totals[category] += converted_size
#
#         for key in specific_totals.keys():
#             if index_name.startswith(key):
#                 specific_totals[key] += converted_size
#
#
#     print("\n--- Totais por Categoria ---")
#     for category, size in category_totals.items():
#         print(f"{category}: {format_size(size)}")
#     print("-" * 40)
#
# def main():
#     index_data = fetch_data(INDEX_URL, AUTH)
#     if index_data:
#         parse_index_data(index_data)
#
# if __name__ == "__main__":
#     main()
#
#
#
#
#     # print("\n--- Detalhes dos Índices ---")
#
#   # print(f"Índice: {index_name}")
#         # print(f"Tamanho original: {original_str}")
#         # print("-" * 40)
#
#
# # print("\n--- Totais por Categoria Específica ---")
#     # for key, size in specific_totals.items():
#     #     print(f"{key}: {format_size(size)}")
#     # print("-" * 40)
#
# # print("\n--- Totais por Categoria Específica ---")
#     # for key, size in specific_totals.items():
#     #     print(f"{key}: {format_size(size)}")
#     # print("-" * 40)