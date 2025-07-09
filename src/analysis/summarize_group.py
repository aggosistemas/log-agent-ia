import os
from datetime import datetime
from google.cloud import firestore

def montar_prompt(logs, servico):
    mensagens = [log.get("mensagem", "") for log in logs]
    conteudo = "\n".join(mensagens[:20])  # limita a 20 mensagens
    prompt = f"""
Você é um assistente técnico. Abaixo estão logs do serviço: {servico}

{conteudo}

Com base nesses logs, forneça:
- Um sumário do que está acontecendo
- Um possível problema identificado
- Uma sugestão técnica para correção ou melhoria
"""
    return prompt.strip()

def salvar_sumario(servico, texto_sumario, origem="openai", quantidade_logs=0):
    client_firestore = firestore.Client(project=os.getenv("GCP_PROJECT_ID"))
    doc_ref = client_firestore.collection("logs_sumarios").document()
    doc_ref.set({
        "servico": servico,
        "sumario": texto_sumario,
        "gerado_por": origem,
        "timestamp": datetime.utcnow(),
        "base_de_dados_usada": quantidade_logs,
        "tipo": "analise-logs"
    })
    print(f"✅ Sumário salvo para '{servico}' (ID: {doc_ref.id})")

def gerar_sumario_para_servico(servico, logs):
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não definida no ambiente.")
    
    client = OpenAI(api_key=api_key)

    print(f"\n🧠 Gerando sumário para o serviço: {servico} (total: {len(logs)} logs)")
    prompt = montar_prompt(logs, servico)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.3,
        messages=[
            {"role": "system", "content": "Você é um especialista em logs."},
            {"role": "user", "content": prompt}
        ]
    )

    resposta = response.choices[0].message.content
    print(resposta)
    salvar_sumario(servico, resposta, quantidade_logs=len(logs))
