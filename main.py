import requests
import json
import os
from datetime import datetime, timedelta

URL = "https://api.systemgame.cc/api/v1/app/random-prize"
ARQUIVO_JSON = 'dados_loterias.json'

def capturar():
    try:
        # Busca o prêmio atual no servidor
        response = requests.get(URL, timeout=30)
        data = response.json().get('data', response.json())
        
        if not data or 'name' not in data:
            return None

        # Ajuste de horário para Santos/Brasília
        fuso_brasilia = datetime.utcnow() - timedelta(hours=3)
        
        return {
            "dia": fuso_brasilia.strftime("%d/%m/%Y"),
            "horario_extracao": data.get("created_at") or fuso_brasilia.strftime("%H:%M"),
            "loteria": data.get("lottery_name") or "Extração Geral",
            "premio_tipo": data.get("prize_type") or "Padrão",
            "ganhador": data.get("name") or "---",
            "valor": data.get("prize") or "R$ 0,00",
            "timestamp_local": fuso_brasilia.isoformat(),
            "suspeito": False
        }
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return None

def salvar(novo):
    if not novo: return
    
    # Carrega o histórico existente ou cria um novo
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            try:
                historico = json.load(f)
                if not isinstance(historico, list): historico = []
            except:
                historico = []
    else:
        historico = []

    # Verifica se já registramos esse exato sorteio (pelo horário e valor)
    if historico:
        ultimo = historico[-1]
        if ultimo['horario_extracao'] == novo['horario_extracao'] and ultimo['valor'] == novo['valor']:
            print("Resultado já registrado anteriormente.")
            return

    # Adiciona e salva
    historico.append(novo)
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)
    print("Sucesso: Novo ganhador salvo no banco de dados!")

if __name__ == "__main__":
    salvar(capturar())