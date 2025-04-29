import logging
import json
import asyncio
import aiohttp

import logging
import os

import ollama
import requests
import random
import subprocess
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

# Konfiguriere Logging
logging.basicConfig(level=logging.DEBUG)

# Webhook-URL aus der .env-Datei
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
MODEL_HUMOR_PATH = os.getenv('MODEL_HUMOR_PATH')
TRIVY_REPORT_PATH = os.getenv('TRIVY_REPORT_PATH')

if not DISCORD_WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK_URL fehlt in der .env-Datei.")
if not MODEL_HUMOR_PATH:
    raise ValueError("MODEL_HUMOR_PATH fehlt in der .env-Datei.")


# Konfiguriere Ollama-Client
ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')  # Falls der Host ein anderer ist
ollama_client = ollama.Client(host=ollama_host)  # Ollama-Client wird hier instanziiert

# Humorvolle Antworten (Beispielantworten)
def load_humor_model():
    humor_responses = [
        "Bug gefunden? Zeit für eine Comedy-Show!",
        "Warum war der Bug traurig? Weil er in einer ungesicherten Codebase lebte!",
        "Dieses Problem ist wie ein Passwort ohne Sonderzeichen – völlig unnötig!",
        "Bug entdeckt? Na, das ist wie ein Ticket für eine Comedy-Show, aber du bist der Hauptakt."
    ]
    return humor_responses

# Funktion zum Senden von Discord-Nachrichten via Webhook
def send_discord_alert(message):
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Nachricht erfolgreich gesendet.")
    else:
        print(f"Fehler: {response.status_code}")

# Funktion zur Log-Analyse mit Ollama CLI
def analyze_logs_with_ollama(logs):
    # Verwende die Ollama CLI lokal, um die Log-Daten zu analysieren
    result = subprocess.run(['ollama', 'analyze', logs], capture_output=True, text=True)
    return result.stdout

# Funktion zum Laden der Trivy-Logs
def load_trivy_logs(log_path="trivy_output.json"):
    try:
        with open(log_path, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
            vulnerabilities = []
            if isinstance(raw_data, dict) and "Results" in raw_data:
                for result in raw_data["Results"]:
                    vulns = result.get("Vulnerabilities", [])
                    if isinstance(vulns, list):
                        vulnerabilities.extend(vulns)
            elif isinstance(raw_data, dict) and "vulnerabilities" in raw_data:
                vulnerabilities = raw_data["vulnerabilities"]

            return vulnerabilities
    except Exception as e:
        logging.error(f"Error loading logs: {e}")
        return []

# Funktion zur Erstellung des Humor-Prompts
def build_prompt_with_logs(logs):
    try:
        with open(MODEL_HUMOR_PATH, "r") as file:
            humor_base = file.read().strip()

        logs_as_text = "\n\n".join([f"Vulnerability {i+1}: {log.get('Title', 'No Title')}" for i, log in enumerate(logs)])

        return (
            f"{humor_base}\n\n"
            f"You are YoBot — a sarcastic AI DevSecOps assistant who turns boring security reports into hilarious, meme-worthy Slack/Discord messages.\n\n"
            f"Now, here's a list of vulnerabilities. For each one, roast it, mock its severity like a drama queen, and end with a funny recommendation.\n\n"
            f"{logs_as_text}\n\n"
            f"🎭 Keep it short, sharp, sassy, and never boring. Go full Sheldon Cooper if needed."
        )
    except Exception as e:
        logging.error(f"Error building prompt: {e}")
        return ""

# Funktion, um die Logs an Ollama zu senden
async def send_prompt_to_ollama(prompt, model="tinyllama", temperature=1.0):
    try:
        # Using the synchronous generate with asyncio.to_thread
        response = await asyncio.to_thread(
            ollama_client.generate,
            model=model,
            prompt=prompt,
            options={'temperature': temperature}
        )
        logging.info("Prompt sent to Ollama successfully.")
        return response.get('response', "No funny response generated.")
    except Exception as e:
        logging.error(f"Ollama generate error: {e}")
        return "Oops, I tried to be funny, but I crashed harder than your CI pipeline."

# Funktion, um Discord-Nachricht zu säubern
def clean_discord_message(text, max_length=1900):
    try:
        cleaned = text.encode("utf-8", "ignore").decode("utf-8").replace('\u0000', '')
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "\n... (truncated)"
        return cleaned
    except Exception as e:
        logging.error(f"Error cleaning message: {e}")
        return ": Message could not be processed."

# Asynchrone Funktion, um Nachricht an Discord zu senden
async def send_discord_message_async(message):
    try:
        payload = {"content": message}
        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers) as response:
                if response.status == 204:
                    logging.info("✅ Message sent to Discord.")
                else:
                    logging.error(f"❌ Discord responded with status: {response.status}")
    except Exception as e:
        logging.error(f"Error sending to Discord: {e}")

# Hauptlogik
async def main():
    try:
        # Beispiel Log-Daten (Hier würdest du echte Logs analysieren)
        logs = load_trivy_logs()

        if not logs:
            logging.error("No valid logs to process.")
            return

        prompt = build_prompt_with_logs(logs)
        if not prompt:
            logging.error("Failed to build prompt.")
            return

        response = await send_prompt_to_ollama(prompt, temperature=1.1)
        final_message = clean_discord_message(response)
        await send_discord_message_async(final_message)

    except Exception as e:
        logging.error(f"Error in main process: {e}")

if __name__ == "__main__":
    asyncio.run(main())
