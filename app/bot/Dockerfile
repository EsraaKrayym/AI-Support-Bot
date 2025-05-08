FROM python:3.10-slim


WORKDIR /app

COPY ./ /app/bot


COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "/app/bot/bot.py"]
