FROM python:3.10-slim

WORKDIR /app

# Trivy installieren
RUN apt-get update && \
    apt-get install -y wget rpm && \
    wget -qO trivy.deb https://github.com/aquasecurity/trivy/releases/latest/download/trivy_0.50.1_Linux-64bit.deb && \
    apt install ./trivy.deb && \
    rm trivy.deb

#COPY app/security_check /app
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

# Kopiere den Rest des Projekts in den Container
COPY ./ /app/security_check

# Setze den Port für den Sicherheits-Check-Service
EXPOSE 8002

# Starte den Sicherheits-Check-Service
CMD ["python", "/app/security_check/security_check.py"]
