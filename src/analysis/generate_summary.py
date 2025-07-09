import os
from dotenv import load_dotenv
from analyze_firestore_logs import fetch_logs, get_firestore_client
from collections import defaultdict
from summarize_group import gerar_sumario_para_servico

load_dotenv()

def agrupar_logs_por_servico(logs):
    agrupado = defaultdict(list)
    for log in logs:
        servico = log.get("servico", "desconhecido")
        agrupado[servico].append(log)
    return agrupado

def executar():
    print("🚀 Iniciando geração de sumários por serviço...\n")
    client = get_firestore_client()
    logs = fetch_logs(client)

    if not logs:
        print("⚠️ Nenhum log encontrado.")
        return

    agrupados = agrupar_logs_por_servico(logs)
    for servico, logs_do_servico in agrupados.items():
        gerar_sumario_para_servico(servico, logs_do_servico)

if __name__ == "__main__":
    executar()
