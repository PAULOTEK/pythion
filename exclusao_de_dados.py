import requests
from datetime import datetime

# Configurações
BASE_URL = 'https://siem.muevy.com'  # Base URL do OpenSearch
AUTH = ('aesadmin', 'gjqC@0n46n6>')  # Nome de usuário e senha
TIMEOUT = 10  # Timeout de requisição em segundos
INDEX_PATTERNS = ["log-ocsf-identity", "log-ocsf-network", "log-ocsf-application"]  # Padrões de índices

# Função para obter a lista de índices
def fetch_indices(base_url, auth):
    """Obtém a lista de índices via API _cat/indices."""
    url = f"{base_url}/_cat/indices?v=true&format=json"
    try:
        response = requests.get(url, auth=auth, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar índices: {e}")
        return []

# Função para excluir índices em massa
def delete_indices(base_url, indices, auth):
    """Exclui uma lista de índices."""
    for index_name in indices:
        delete_url = f"{base_url}/{index_name}"
        try:
            response = requests.delete(delete_url, auth=auth, timeout=TIMEOUT)
            response.raise_for_status()
            print(f"Índice {index_name} excluído com sucesso.")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao excluir índice {index_name}: {e}")

# Função principal
def delete_indices_by_patterns():
    """Busca e exclui índices que correspondam aos padrões definidos em INDEX_PATTERNS."""
    indices = fetch_indices(BASE_URL, AUTH)
    if not indices:
        print("Nenhum índice encontrado ou erro ao buscar índices.")
        return

    indices_to_delete = []  # Lista para armazenar os índices que serão excluídos

    for index in indices:
        index_name = index.get("index")  # Nome do índice
        if index_name:
            # Verifica se o índice começa com algum dos padrões definidos
            for pattern in INDEX_PATTERNS:
                if index_name.startswith(pattern):
                    # Opcional: Verifica se contém uma data no formato YYYY-MM
                    try:
                        date_part = index_name.split(f"{pattern}-")[1]
                        index_date = datetime.strptime(date_part, "%Y-%m")
                        indices_to_delete.append(index_name)
                        break  # Não precisa verificar outros padrões
                    except (IndexError, ValueError):
                        print(f"Índice {index_name} não segue o formato esperado. Ignorando...")

    # Exclui todos os índices encontrados
    if indices_to_delete:
        print(f"Iniciando exclusão de {len(indices_to_delete)} índices: {indices_to_delete}")
        delete_indices(BASE_URL, indices_to_delete, AUTH)
    else:
        print("Nenhum índice com os padrões especificados foi encontrado para exclusão.")

# Executar script
if __name__ == "__main__":
    delete_indices_by_patterns()
