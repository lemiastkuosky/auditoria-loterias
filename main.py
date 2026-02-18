import requests
import json
import os
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES ---
URL = "https://api.systemgame.cc/api/v1/app/random-prize"
ARQUIVO_JSON = 'dados_loterias.json'

# Token Válido (Atualizado)
HEADERS = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjE3OTg2OCwiaWF0IjoxNzcxNDI4MDM2LCJleHAiOjE3NzQwMjAwMzZ9.NGO5X3txXXqse3b3G7jPbIvhBfYo60E5e74Q5mXdVH4',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def capturar():
    print(f"🔄 Conectando ao servidor...")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            raw = response.json()
            data_interna = raw.get('data', {})

            # --- DADOS DETALHADOS ---
            nome_ganhador = raw.get('winner', '---')
            # Se o nome for "Unidade: X", tenta pegar nome real se existir, ou mantém
            if "Unidade" in nome_ganhador and 'name' in data_interna:
                 nome_ganhador = data_interna['name']

            numero_jogado = data_interna.get('numero', '---') # O NÚMERO EXATO (ex: 032)
            modalidade = data_interna.get('modalidade', 'Prêmio') # EX: CENTENA, MILHAR
            nome_loteria = data_interna.get('loteriaTitle', 'Extração Geral')
            valor_bruto = raw.get('prize', 0)
            horario_servidor = raw.get('created_at') 

            # Formatação de Valor
            try:
                val_float = float(valor_bruto)
                valor_formatado = f"R$ {val_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            except:
                valor_formatado = f"R$ {valor_bruto}"

            fuso_brasilia = datetime.utcnow() - timedelta(hours=3)
            
            registro = {
                "dia": fuso_brasilia.strftime("%d/%m/%Y"),
                "horario_extracao": horario_servidor.split(' ')[1] if ' ' in horario_servidor else fuso_brasilia.strftime("%H:%M"),
                "loteria": nome_loteria,
                "modalidade": modalidade,  # Campo novo
                "numero_sorteado": numero_jogado, # Campo novo
                "ganhador": nome_ganhador,
                "valor": valor_formatado,
                "timestamp_local": fuso_brasilia.isoformat(),
                "suspeito": False
            }
            
            print(f"✅ CAPTURADO: {registro['modalidade']} - Nº {registro['numero_sorteado']} - {registro['valor']}")
            return registro
        
        elif response.status_code == 401:
            print("❌ Erro 401: Token expirado.")
            return None
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Erro Crítico: {e}")
        return None

def salvar(novo):
    if not novo: return
    
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            try:
                historico = json.load(f)
                if not isinstance(historico, list): historico = []
            except:
                historico = []
    else:
        historico = []

    # Validação Anti-Duplicidade
    if historico:
        ultimo = historico[-1]
        # Compara Loteria, Valor e Número para saber se é o mesmo prêmio
        if (ultimo.get('loteria') == novo['loteria'] and 
            ultimo.get('valor') == novo['valor'] and 
            ultimo.get('numero_sorteado') == novo['numero_sorteado']):
            print("ℹ️ Dado já existente.")
            return

    historico.append(novo)
    
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)
    print("💾 BANCO DE DADOS ATUALIZADO!")

if __name__ == "__main__":
    salvar(capturar())