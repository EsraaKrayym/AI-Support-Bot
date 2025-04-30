# Verwende ein leichtes Python-Image
FROM python:3.8-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# Kopiere requirements.txt und installiere die Abhängigkeiten
4COPY ../app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Projekts in den Container
COPY . /app

# Setze den Port für den Sicherheits-Check-Service
EXPOSE 8002

# Starte den Sicherheits-Check-Service
CMD ["python", "security_check.py"]
