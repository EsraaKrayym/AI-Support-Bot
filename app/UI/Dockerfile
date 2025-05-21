FROM python:3.10-slim

WORKDIR /app

# Install requirements
COPY app/UI/requirements.txt ./requirements_ui.txt
COPY app/bot/requirements.txt ./requirements_bot.txt
RUN pip install --no-cache-dir -r requirements_ui.txt \
    && pip install --no-cache-dir -r requirements_bot.txt

# Copy source code
COPY app/UI/app.py ./UI/app.py
COPY app/bot ./bot

# Add shared model file
COPY model_humor.txt /app/shared/model_humor.txt

# Set working dir so Python finds `bot` properly
ENV PYTHONPATH=/app
EXPOSE 7860
# Run app
CMD ["python", "UI/app.py"]
