# Spectra AI Agent

Agente de IA desenvolvido com o framework **Agno**, especializado em monitoramento tecnológico. Responde perguntas sobre recursos do sistema, clima, criptomoedas e saúde de websites via CLI ou interface web.

---

## Tools implementadas

| Tool | Descrição |
|---|---|
| `get_system_stats` | CPU, RAM, disco e top 5 processos por consumo (via psutil) |
| `get_weather` | Clima atual de qualquer cidade (Open-Meteo API — sem chave) |
| `get_crypto_price` | Cotação de criptomoedas em USD e BRL (CoinGecko API — sem chave) |
| `check_website_health` | Status HTTP, latência e headers de qualquer URL |

---

## Pré-requisitos

- Python 3.10+
- Chave da **Gemini API** (ou Ollama rodando localmente)

---

## Instalação

```bash
# 1. Clone ou extraia o projeto
cd spectra-ai-agent

# 2. Crie e ative o ambiente virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env e insira sua GEMINI_API_KEY
```

---

## Configuração (.env)

```env
MODEL_PROVIDER=gemini          # "gemini" ou "ollama"
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.0-flash
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:0.6b
SESSION_ID=spectra-ai-cli
DB_PATH=spectra-ai.db
FLASK_SECRET_KEY=string-aleatoria
FLASK_PORT=5000
```

---

## Execução via CLI

```bash
python main.py
```

**Exemplo de conversa:**

```
Você: Como está o uso do sistema agora?
Spectra AI: CPU: 14% | RAM: 7,2 GB / 16 GB (45%) | Disco: 120 GB / 500 GB (24%)...

Você: Qual o preço do Bitcoin hoje?
Spectra AI: Bitcoin (BTC): $67.420 USD / R$ 342.890 BRL | Variação 24h: +2,3%...

Você: sair
```

---

## Interface web (bônus)

```bash
python app.py
```

Acesse: [http://localhost:5000](http://localhost:5000)

---

## Docker (bônus)

```bash
# Build da imagem
docker build -t spectra-ai-agent .

# Executar CLI (necessário .env configurado)
docker run -it --env-file .env spectra-ai-agent

# Executar interface web
docker run -p 5000:5000 --env-file .env spectra-ai-agent python app.py
```

---

## Estrutura do projeto

```
spectra-ai-agent/
├── main.py           # Ponto de entrada CLI
├── app.py            # Interface web Flask
├── tools.py          # 4 tools do agente
├── requirements.txt
├── .env.example      # Modelo de configuração
├── .env              # Configuração real (não commitar)
├── Dockerfile
├── README.md
└── templates/
    └── index.html    # Interface web
```
