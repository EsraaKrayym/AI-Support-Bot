# Verwende ein leichtes Python-Image
FROM python:3.8-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# Kopiere die requirements.txt ins Arbeitsverzeichnis
COPY ../app/requirements.txt /app/requirements.txt

# Installiere die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Projekts in den Container
COPY . /app

# Setze den Port für den Bot
EXPOSE 8000

# Starte den Bot
CMD ["python", "bot.py"]
