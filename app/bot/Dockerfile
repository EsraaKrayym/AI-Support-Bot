FROM python:3.10-slim

WORKDIR /app/bot

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Korrigierter Pfad
COPY ./app/bot/bot.py .
# Falls nötig: extra Dateien aus dem übergeordneten Ordner
COPY ../trivy_output.json /app/
COPY ../model_humor.txt /app/

CMD ["python", "bot.py"]
