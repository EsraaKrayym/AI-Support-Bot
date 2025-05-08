FROM python:3.10-slim

WORKDIR /app

# Trivy installieren
RUN apt-get update && \
    apt-get install -y wget rpm && \
    wget -qO trivy.deb https://github.com/aquasecurity/trivy/releases/latest/download/trivy_0.50.1_Linux-64bit.deb && \
    apt install ./trivy.deb && \
    rm trivy.deb

COPY app/security_check /app
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "security_check.py"]
