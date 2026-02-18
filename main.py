import requests
import json
import os
from datetime import datetime, timedelta

# Configurações
URL = "https://api.systemgame.cc/api/v1/app/random-prize"
ARQUIVO_JSON = 'dados_loterias.json'

def capturar_dados():
    try:
        response = requests.get(URL, timeout=20)
        data = response.json().get('data', response.json())
        
        if not data or 'name' not in data:
            return None

        # Ajuste para Horário de Brasília (UTC -3)
        fuso_brasilia = datetime.utcnow() - timedelta(hours=3)
        
        return {
            "dia": fuso_brasilia.strftime("%d/%m/%Y"),
            "horario_registro": fuso_brasilia.strftime("%H:%M:%S"),
            "horario_extracao": data.get("created_at") or fuso_brasilia.strftime("%H:%M"),
            "loteria": data.get("lottery_name") or "Extração Geral",
            "ganhador": data.get("name"),
            "valor": data.get("prize"),
            "timestamp_local": fuso_brasilia.isoformat()
        }
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return None

def salvar(novo):
    if not novo: return
    
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            historico = json.load(f)
    else:
        historico = []

    # Bloqueia duplicados: só salva se o ganhador E o valor forem diferentes do último
    if historico and historico[-1]['ganhador'] == novo['ganhador'] and historico[-1]['valor'] == novo['valor']:
        print("Sorteio já auditado. Pulando...")
        return

    historico.append(novo)
    
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)
    print(f"✅ Sucesso: {novo['ganhador']} registrado às {novo['horario_registro']}")

if __name__ == "__main__":
    salvar(capturar_dados())