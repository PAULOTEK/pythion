#!/usr/bin/env python3

import json
import sys
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor
from kubernetes import client, config

def list_platform_pods():
    """Lista os pods disponíveis no cluster cujo nome contém 'platform'."""
    try:
        config.load_kube_config()  # Carrega a configuração do kubeconfig
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch=False)
        return [
            {"name": item.metadata.name, "status": item.status.phase}
            for item in pods.items
            if "platform" in item.metadata.name and item.status.phase == "Running"
        ]
    except Exception as e:
        print(f"Erro ao listar pods: {e}", file=sys.stderr)
        sys.exit(1)

def generate_logs(pod_name):
    """Gera os logs do pod especificado e salva em um arquivo temporário."""
    temp_dir = tempfile.gettempdir()
    log_file = os.path.join(temp_dir, f"{pod_name}.log")

    try:
        config.load_kube_config()  # Carrega a configuração do kubeconfig
        v1 = client.CoreV1Api()
        logs = v1.read_namespaced_pod_log(name=pod_name, namespace="default", tail_lines=500)
        with open(log_file, "w") as log:
            log.write(logs)
        print(f"Log gerado com sucesso: {log_file}")
    except Exception as e:
        print(f"Erro ao gerar logs do pod {pod_name}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    while True:
        pods = list_platform_pods()

        if not pods:
            print("Nenhum pod 'platform' disponível encontrado.")
            sys.exit(0)

        print("\nPods disponíveis:")
        for i, pod in enumerate(pods, start=1):
            print(f"{i}. {pod['name']} (Status: {pod['status']})")

        try:
            selection = int(input("Selecione o número do pod para gerar logs (ou 0 para sair): "))
            if selection == 0:
                print("Encerrando...")
                break
            elif 1 <= selection <= len(pods):
                generate_logs(pods[selection - 1]["name"])
            else:
                print("Seleção inválida.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número.")

if __name__ == "__main__":
    main()