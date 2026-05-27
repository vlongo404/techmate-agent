import os
import uuid
from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv
from agno.agent import Agent
from agno.db.sqlite.sqlite import SqliteDb

from tools import get_system_stats, get_weather, get_crypto_price, check_website_health

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "techmate-secret-change-in-prod")

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
DB_PATH = os.getenv("DB_PATH", "techmate.db")

DESCRIPTION = """
Você é TechMate, um assistente tecnológico especializado. Você pode:
- Monitorar recursos do sistema (CPU, RAM, disco, processos)
- Consultar o clima atual de qualquer cidade do mundo
- Verificar preços e dados de mercado de criptomoedas
- Checar se websites estão online e medir tempo de resposta

Sempre responda em português, de forma clara e objetiva.
Use as ferramentas disponíveis para fornecer informações reais e atualizadas.
""".strip()


def build_model():
    if MODEL_PROVIDER == "ollama":
        from agno.models.ollama import OllamaResponses
        return OllamaResponses(id=OLLAMA_MODEL, host=OLLAMA_HOST, api_key="ollama")
    else:
        from agno.models.google import Gemini
        return Gemini(id=GEMINI_MODEL, api_key=GEMINI_API_KEY)


def get_agent(session_id: str) -> Agent:
    return Agent(
        model=build_model(),
        tools=[get_system_stats, get_weather, get_crypto_price, check_website_health],
        db=SqliteDb(db_file=DB_PATH),
        session_id=session_id,
        add_history_to_context=True,
        num_history_runs=10,
        description=DESCRIPTION,
        markdown=True,
    )


@app.route("/")
def index():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Mensagem vazia"}), 400

    session_id = session.get("session_id", "web-default")
    agent = get_agent(session_id)

    response = agent.run(user_message)
    reply = response.content if hasattr(response, "content") else str(response)

    return jsonify({"response": reply or "Sem resposta."})


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
