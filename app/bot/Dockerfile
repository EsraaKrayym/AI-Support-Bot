# Verwende ein leichtes Python-Image
FROM python:3.9-slim


# Arbeitsverzeichnis setzen
WORKDIR /app

# Kopiere die requirements.txt ins Arbeitsverzeichnis
COPY requirements.txt /app/requirements.txt

# Installiere die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Projekts in den Container
COPY ./ /app/bot
COPY trivy_output.json /app/
COPY  model_humor.txt /app/

# Setze den Port für den Bot
EXPOSE 8000

# Starte den Bot
CMD ["python", "/app/bot/bot.py"]
