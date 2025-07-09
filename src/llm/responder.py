import os
from openai import OpenAI

def responder_ia(pergunta_usuario, contexto_sumarios):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada")

    client = OpenAI(api_key=api_key)

    contexto = "\n".join([s["sumario"] for s in contexto_sumarios if "sumario" in s])

    prompt = f"""
Você é um assistente técnico treinado para analisar logs e ajudar engenheiros de software.
Aqui está um resumo de eventos recentes extraídos dos logs:

{contexto}

Com base nessas informações, responda à pergunta abaixo com clareza e foco técnico:

{pergunta_usuario}
"""

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.4,
        messages=[
            {"role": "system", "content": "Você é um assistente técnico confiável."},
            {"role": "user", "content": prompt}
        ]
    )

    return resposta.choices[0].message.content
