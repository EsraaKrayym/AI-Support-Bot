FROM python:3.10-slim


WORKDIR /app

COPY app/ai_analysis /app
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "ai_analysis.py"]
