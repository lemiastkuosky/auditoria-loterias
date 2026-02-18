import requests
import json
import os
from datetime import datetime, timedelta

URL = "https://api.systemgame.cc/api/v1/app/random-prize"
ARQUIVO_JSON = 'dados_loterias.json'

def capturar():
    try:
        response = requests.get(URL, timeout=20)
        data = response.json().get('data', response.json())
        if not data: return None

        # Registra o horário exato de Santos/Brasília
        fuso_brasilia = datetime.utcnow() - timedelta(hours=3)
        
        return {
            "dia": fuso_brasilia.strftime("%d/%m/%Y"),
            "horario_extracao": data.get("created_at") or fuso_brasilia.strftime("%H:%M"),
            "loteria": data.get("lottery_name") or "Extração Geral",
            "premio_tipo": data.get("prize_type") or "Padrão",
            "ganhador": data.get("name") or "---",
            "valor": data.get("prize") or "R$ 0,00",
            "timestamp_local": fuso_brasilia.isoformat(), # VITAL PARA O LED FICAR VERDE
            "suspeito": False
        }
    except:
        return None

def salvar(novo):
    if not novo: return
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            historico = json.load(f)
    else:
        historico = []

    # Evita duplicados
    if historico and historico[-1]['horario_extracao'] == novo['horario_extracao'] and \
       historico[-1]['loteria'] == novo['loteria']:
        return

    historico.append(novo)
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    salvar(capturar())