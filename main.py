import os
import sys
from dotenv import load_dotenv
from agno.agent import Agent
from agno.db.sqlite.sqlite import SqliteDb

from tools import get_system_stats, get_weather, get_crypto_price, check_website_health

load_dotenv(override=True)

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
SESSION_ID = os.getenv("SESSION_ID", "spectra-cli")
DB_PATH = os.getenv("DB_PATH", "spectra.db")


def build_model():
    if MODEL_PROVIDER == "ollama":
        from agno.models.ollama import OllamaResponses
        return OllamaResponses(id=OLLAMA_MODEL, host=OLLAMA_HOST, api_key="ollama")
    else:
        from agno.models.google import Gemini
        return Gemini(id=GEMINI_MODEL, api_key=GEMINI_API_KEY)


DESCRIPTION = """
Você é Spectra AI, um assistente tecnológico especializado. Você pode:
- Monitorar recursos do sistema (CPU, RAM, disco, processos)
- Consultar o clima atual de qualquer cidade do mundo
- Verificar preços e dados de mercado de criptomoedas
- Checar se websites estão online e medir tempo de resposta

Sempre responda em português, de forma clara e objetiva.
Use as ferramentas disponíveis para fornecer informações reais e atualizadas.
Nunca invente dados — use sempre as tools.
""".strip()


def main():
    model = build_model()

    agent = Agent(
        model=model,
        tools=[get_system_stats, get_weather, get_crypto_price, check_website_health],
        db=SqliteDb(db_file=DB_PATH),
        session_id=SESSION_ID,
        add_history_to_context=True,
        num_history_runs=10,
        description=DESCRIPTION,
        markdown=True,
    )

    print("=" * 58)
    print("   Spectra AI — Assistente Tecnológico")
    print("=" * 58)
    print(f"   Modelo : {MODEL_PROVIDER.upper()} | Sessão: {SESSION_ID}")
    print("   Tools  : sistema · clima · cripto · website")
    print("=" * 58)
    print("   Digite 'sair' ou pressione Ctrl+C para encerrar\n")

    while True:
        try:
            user_input = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nEncerrando Spectra AI. Até logo!")
            sys.exit(0)

        if not user_input:
            continue

        if user_input.lower() in ("sair", "exit", "quit", "q"):
            print("Encerrando Spectra AI. Até logo!")
            break

        print("\nSpectra AI:", end=" ", flush=True)
        agent.print_response(user_input, stream=True)
        print()


if __name__ == "__main__":
    main()
