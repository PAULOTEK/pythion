#!/usr/bin/env python3

import subprocess
import json
import sys
import os

LOG_DIRECTORY = r"C:\Users\Paulo\OneDrive\Documentos\logs"

# Cria o diretório de logs, se não existir
os.makedirs(LOG_DIRECTORY, exist_ok=True)

def list_platform_pods():
    """Lista os pods disponíveis no cluster cujo nome contém 'platform'."""
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        pods = json.loads(result.stdout)
        return [
            {"name": item["metadata"]["name"], "status": item["status"]["phase"]}
            for item in pods.get("items", [])
            if "platform" in item["metadata"]["name"] and item["status"]["phase"] == "Running"
        ]
    except Exception as e:
        print(f"Erro ao listar pods: {e}", file=sys.stderr)
        sys.exit(1)

def generate_logs(pod_name):
    """Gera os logs do pod especificado e salva no diretório de logs."""
    log_file = os.path.join(LOG_DIRECTORY, f"{pod_name}.log")

    try:
        with open(log_file, "w") as log:
            subprocess.run(
                ["kubectl", "logs", "--tail=500", pod_name],
                stdout=log,
                check=True
            )
        print(f"Log gerado com sucesso: {log_file}")
    except subprocess.CalledProcessError as e:
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