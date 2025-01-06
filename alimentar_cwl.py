from opensearchpy import OpenSearch
from datetime import datetime
import time

# Configurações de conexão
BASE_URL = 'https://siem.muevy.com'  # Substitua pelo seu URL base do OpenSearch
AUTH = ('aesadmin', 'gjqC@0n46n6>')  # Substitua pelo seu nome de usuário e senha

# Nome do alias
alias_name = "1008-muevy-transactions-log"

# Conecte-se ao OpenSearch
es = OpenSearch(
    [BASE_URL],
    http_auth=AUTH,
    use_ssl=True,
    verify_certs=True,
    ssl_show_warn=False
)

def atualizar_alias():
    # Obtém a data atual
    today = datetime.now()

    # Formata a data no padrão 'cwl-YYYY.MM.DD'
    index_name = f"cwl-{today.strftime('%Y.%m.%d')}"

    # Atualiza o alias para apontar para o novo índice
    actions = [
        {"remove": {"index": "*", "alias": alias_name}},  # Remove o alias de todos os índices
        {"add": {"index": index_name, "alias": alias_name}}  # Adiciona o alias ao novo índice
    ]

    response = es.indices.update_aliases({"actions": actions})
    print(response)

if __name__ == "__main__":
    while True:
        atualizar_alias()
        time.sleep(5)  # Aguarda 5 segundos antes de executar novamente
