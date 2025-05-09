# app/security_check/Dockerfile

FROM python:3.10-slim

# Arbeitsverzeichnis
WORKDIR /app/security_check

# System-Pakete für Trivy installieren
RUN apt-get update && \
    apt-get install -y curl gnupg lsb-release wget && \
    # Trivy Repository hinzufügen
    wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add - && \
    echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" \
      | tee /etc/apt/sources.list.d/trivy.list && \
    apt-get update && \
    apt-get install -y trivy && \
    rm -rf /var/lib/apt/lists/*

# Pre-warm Trivy-Datenbank-Cache (optional)
RUN mkdir -p /root/.cache/trivy && \
    trivy image \
      --cache-dir /root/.cache/trivy \
      --format json \
      --quiet alpine:latest || true

# Python-Abhängigkeiten installieren
COPY app/security_check/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY app/security_check/security_check.py .

# Standardkommando
CMD ["python", "security_check.py"]
