FROM python:3.10-slim


WORKDIR /app

COPY ./ /app/bot


COPY requirements.txt /app/requirements.txt

COPY trivy_output.json /app/
COPY  model_humor.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "/app/bot/bot.py"]
