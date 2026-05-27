FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Garante que o .env existe (usuário deve montar o arquivo real)
RUN cp -n .env.example .env 2>/dev/null || true

ENV MODEL_PROVIDER=gemini

# CLI por padrão; use CMD ["python", "app.py"] para a interface web
CMD ["python", "main.py"]
