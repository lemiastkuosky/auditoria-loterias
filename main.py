import requests
import json
import os
from datetime import datetime, timedelta

# Configurações Iniciais
URL = "https://api.systemgame.cc/api/v1/app/random-prize"
ARQUIVO_JSON = 'dados_loterias.json'

# AQUI ESTÁ O SEGREDO: O Cabeçalho com a sua chave (Token)
HEADERS = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjE3OTg2OCwiaWF0IjoxNzcxNDI4MDM2LCJleHAiOjE3NzQwMjAwMzZ9.NGO5X3txXXqse3b3G7jPbIvhBfYo60E5e74Q5mXdVH4',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def capturar():
    print(f"🔄 Conectando ao servidor com credenciais seguras...")
    try:
        # Envia a requisição COM a chave de autorização
        response = requests.get(URL, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            data = response.json().get('data', response.json())
            
            # Validação extra para garantir que veio dado real
            if not data or 'name' not in data:
                print("⚠️ Servidor autorizado, mas retornou lista vazia (sem ganhador no momento).")
                return None

            # Ajuste de Fuso Horário (Santos/Brasília)
            fuso_brasilia = datetime.utcnow() - timedelta(hours=3)
            
            registro = {
                "dia": fuso_brasilia.strftime("%d/%m/%Y"),
                "horario_extracao": data.get("created_at") or fuso_brasilia.strftime("%H:%M"),
                "loteria": data.get("lottery_name") or "Extração Geral",
                "premio_tipo": data.get("prize_type") or "Padrão",
                "ganhador": data.get("name") or "---",
                "valor": data.get("prize") or "R$ 0,00",
                "timestamp_local": fuso_brasilia.isoformat(),
                "suspeito": False
            }
            print(f"✅ SUCESSO! Ganhador detectado: {registro['ganhador']} ({registro['valor']})")
            return registro
        
        elif response.status_code == 401:
            print("❌ Erro 401: O Token venceu ou foi bloqueado. Precisa gerar um novo.")
            return None
        else:
            print(f"❌ Erro desconhecido: Código {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Erro Crítico na conexão: {e}")
        return None

def salvar(novo):
    if not novo: return
    
    # Lógica inteligente de salvamento
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            try:
                historico = json.load(f)
                if not isinstance(historico, list): historico = []
            except:
                historico = []
    else:
        historico = []

    # Evita duplicidade exata
    if historico:
        ultimo = historico[-1]
        if ultimo.get('horario_extracao') == novo['horario_extracao'] and ultimo.get('valor') == novo['valor']:
            print("ℹ️ Este resultado já estava salvo. Aguardando próximo...")
            return

    historico.append(novo)
    
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)
    print("💾 BANCO DE DADOS ATUALIZADO NO GITHUB!")

if __name__ == "__main__":
    salvar(capturar())