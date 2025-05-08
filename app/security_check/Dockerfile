FROM python:3.10-slim

WORKDIR /app

# Installiere Trivy
RUN apt-get update && apt-get install -y \
    curl \
    && curl -sfL https://github.com/aquasecurity/trivy/releases/download/v0.34.0/trivy_0.34.0_Linux-64bit.deb -o trivy.deb \
    && dpkg -i trivy.deb \
    && rm trivy.deb \
    && apt-get clean
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

# Kopiere den Rest des Projekts in den Container
COPY ./ /app/security_check
#COPY ./security_check /app/security_check

# Setze den Port für den Sicherheits-Check-Service
EXPOSE 8002

# Starte den Sicherheits-Check-Service
CMD ["python", "/app/security_check/security_check.py"]
