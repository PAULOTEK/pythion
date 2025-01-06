from opensearchpy import OpenSearch
from datetime import datetime
import time
import os

# Configurações de conexão
BASE_URL = os.getenv("OPENSEARCH_URL", "https://siem.muevy.com")  # URL base do OpenSearch
USER = os.getenv("OPENSEARCH_USER", "aesadmin")  # Usuário do OpenSearch
PASSWORD = os.getenv("OPENSEARCH_PASSWORD", "gjqC@0n46n6>")  # Senha do OpenSearch

# Nome do alias
alias_name = "1008-muevy-transactions-log"

# Conectar-se ao OpenSearch
es = OpenSearch(
    [BASE_URL],
    http_auth=(USER, PASSWORD),
    use_ssl=True,
    verify_certs=True,
    ssl_show_warn=False
)


def debug_log(msg):
    """Função auxiliar para adicionar logs de depuração."""
    print(f"[DEBUG] {msg}")


def criar_indice(index_name):
    """Cria um índice no OpenSearch."""
    try:
        # Exemplo de configuração de mapeamento para o novo índice
        index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            }
        }
        # Criação do índice
        es.indices.create(index=index_name, body=index_settings)
        debug_log(f"Índice {index_name} criado com sucesso.")
    except Exception as e:
        debug_log(f"Erro ao criar índice {index_name}: {e}")


def atualizar_alias(index_name):
    """Atualiza o alias para o novo índice."""
    try:
        # Detalha as ações para atualizar os aliases
        actions = [
            {"remove": {"index": "*", "alias": alias_name}},  # Remove o alias de todos os índices
            {"add": {"index": index_name, "alias": alias_name}}  # Adiciona o alias ao novo índice
        ]
        debug_log(f"Ações para atualizar alias: {actions}")

        # Envia a solicitação para atualizar os aliases
        response = es.indices.update_aliases(body={"actions": actions})

        debug_log(f"Resposta do OpenSearch: {response}")

        if response.get('acknowledged', False):
            print(f"Alias atualizado com sucesso para o índice: {index_name}")
        else:
            print("Falha ao atualizar o alias. Detalhes: ", response)

    except Exception as e:
        print(f"Erro ao atualizar alias: {e}")
        debug_log(f"Erro completo: {e}")


def verificar_e_atualizar_alias():
    """Verifica se o índice do dia existe e cria se necessário. Atualiza o alias."""
    today = datetime.now()
    index_name = f"cwl-{today.strftime('%Y.%m.%d')}"

    debug_log(f"Nome do índice para atualizar o alias: {index_name}")

    # Verifica se o índice já existe
    if not es.indices.exists(index=index_name):
        print(f"Índice {index_name} não existe. Criando o índice...")
        criar_indice(index_name)
        atualizar_alias(index_name)  # Atualiza o alias após criar o índice
    else:
        debug_log(f"Índice {index_name} já existe. Nenhuma ação necessária.")


if __name__ == "__main__":
    while True:
        verificar_e_atualizar_alias()
        debug_log("Aguardando 5 minutos para a próxima execução...")
        time.sleep(300)  # Aguarda 5 minutos antes de verificar novamente


# https://siem.muevy.com/_cat/indices