FROM python:3.10-slim

WORKDIR /app/ai_analysis

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Korrigierter Pfad
COPY ./app/ai_analysis/ai_analysis.py .

CMD ["python", "ai_analysis.py"]
