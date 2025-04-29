# Base Image
FROM python:3.8-slim

WORKDIR /app

# Install dependencies
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY .. /app

EXPOSE 8000

CMD ["python", "app/bot.py"]
