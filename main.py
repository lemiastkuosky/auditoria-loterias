import requests
import json
import os
from datetime import datetime

# URL da API que você descobriu
URL = "https://api.systemgame.cc/api/v1/app/random-prize"

def capturar():
    try:
        # Tenta acessar a API
        response = requests.get(URL, timeout=15)
        data = response.json().get('data', response.json())
        
        if not data or 'name' not in data:
            return None

        agora = datetime.now()
        
        return {
            "dia": agora.strftime("%d/%m/%Y"),
            "horario_extracao": data.get("created_at") or agora.strftime("%H:%M"),
            "loteria": data.get("lottery_name") or "Loteria Padrão",
            "ganhador": data.get("name"),
            "valor": data.get("prize"),
            "timestamp": agora.isoformat()
        }
    except:
        return None

def atualizar_banco(novo_registro):
    if not novo_registro: return

    arquivo = 'dados_loterias.json'
    
    # Carrega dados existentes
    if os.path.exists(arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            historico = json.load(f)
    else:
        historico = []

    # Evita duplicados (checa se o ganhador e horário são os mesmos do último registro)
    if historico and historico[-1]['ganhador'] == novo_registro['ganhador'] and historico[-1]['horario_extracao'] == novo_registro['horario_extracao']:
        print("Dados já registrados. Pulando...")
        return

    historico.append(novo_registro)
    
    # Salva de volta no JSON
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)
    print(f"Sucesso: {novo_registro['ganhador']} registrado.")

if __name__ == "__main__":
    registro = capturar()
    atualizar_banco(registro)