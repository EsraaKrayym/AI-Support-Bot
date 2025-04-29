# Verwende ein leichtes Python-Image
FROM python:3.8-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# Kopiere requirements.txt und installiere die Abhängigkeiten
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Projekts in den Container
COPY . /app

# Setze den Port, den der KI-Analyse-Service verwenden wird
EXPOSE 8001

# Starte den KI-Analyse-Service
CMD ["python", "ai_analysis.py"]
