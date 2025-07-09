import os
import pandas as pd
from google.cloud import firestore
from datetime import datetime

# Define o nome da coleção
COLECAO_LOGS = "logs_pipeline"

def get_firestore_client():
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("Variável GCP_PROJECT_ID não configurada")
    return firestore.Client(project=project_id)

def fetch_logs(client):
    print(f"📥 Coletando logs da coleção: {COLECAO_LOGS}")
    docs = client.collection(COLECAO_LOGS).stream()

    registros = []
    for doc in docs:
        data = doc.to_dict()
        data['doc_id'] = doc.id
        registros.append(data)

    print(f"✅ Total de documentos encontrados: {len(registros)}")
    return registros

def analisar_logs(logs):
    df = pd.DataFrame(logs)

    # Converte o timestamp se existir
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    print("\n📊 Quantidade por nível:")
    print(df["nivel"].value_counts())

    print("\n📊 Quantidade por serviço:")
    print(df["servico"].value_counts())

    print("\n📊 Top mensagens:")
    print(df["mensagem"].value_counts().head(5))

    # Exporta CSV (opcional)
    now = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = f"logs_agrupados_{now}.csv"
    df.to_csv(output_file, index=False)
    print(f"\n📁 Logs exportados para: {output_file}")

if __name__ == "__main__":
    print("🚀 Iniciando análise de logs do Firestore...\n")

    client = get_firestore_client()
    logs = fetch_logs(client)

    if logs:
        analisar_logs(logs)
    else:
        print("⚠️ Nenhum log encontrado.")
