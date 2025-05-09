FROM python:3.10-slim

WORKDIR /app/bot

FROM python:3.10-slim
WORKDIR /app/bot

COPY app/bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Dein Bot-Skript
COPY app/bot/bot.py .

# Modell ins Volume legen
COPY model_humor.txt /app/shared/model_humor.txt

CMD ["python", "bot.py"]
