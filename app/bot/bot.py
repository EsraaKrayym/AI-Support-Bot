import logging
import json
import asyncio
import aiohttp
import os
import discord
import requests
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
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")


if not DISCORD_WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK_URL fehlt in der .env-Datei.")
if not MODEL_HUMOR_PATH:
    raise ValueError("MODEL_HUMOR_PATH fehlt in der .env-Datei.")


# Konfiguriere Ollama-Client
#ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')  # Falls der Host ein anderer ist
#ollama_client = ollama.Client(host=ollama_host)  # Ollama-Client wird hier instanziiert


# Erstelle die Intents
intents = discord.Intents.default()  # Aktiviert standardmäßig die gängigen Ereignisse
intents.messages = True  # Aktiviert das Empfangen von Nachrichten
intents.guilds = True    # Aktiviert das Empfangen von Serverereignissen

# Erstelle den Discord-Client mit den Intents
#client = discord.Client(intents=discord.Intents.default())



#@client.event
#async def on_ready():
 #   print(f'Bot ist eingeloggt als {client.user}')


# Vordefinierte Fragen, auf die der Bot antworten soll
def get_response(message_content):
    responses = {
        "warum konnte die lokalseite nicht geöffnet werden?": "Die Seite konnte nicht geöffnet werden, weil es eine Sicherheitslücke gibt. Bitte aktualisiere den Webserver!",
        "wie behebe ich die Sicherheitslücke in nginx?": "Aktualisiere nginx auf die neueste Version, um die Pufferüberlauf-Schwachstelle zu beheben.",
        "was sind die neuesten Trivy-Sicherheitslücken?": "Die neuesten Trivy-Scans zeigen mehrere Schwachstellen in OpenSSL und Apache.",
        "was ist eine XSS-Schwachstelle?": "Eine XSS-Schwachstelle (Cross-Site Scripting) ermöglicht es Angreifern, bösartigen JavaScript-Code in eine Webseite einzuschleusen."
    }

    # Wenn die Nachricht eine der vordefinierten Fragen ist, gib die Antwort zurück
    return responses.get(message_content.lower(), None)


#@client.event
#async def on_message(message):
   # if message.author == client.user:
        #return

    # Hole die Antwort basierend auf der Nachricht
    response = get_response(message.content)

    #if response:
        # Sende die Antwort an den Discord-Channel
        #await message.channel.send(response)
    #else:
     #   logging.debug(f"Bot hat keine Antwort auf: {message.content}")




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
def load_trivy_logs(log_path=None):
    path = log_path or TRIVY_REPORT_PATH
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            raw_data = json.load(f)
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
        with open(MODEL_HUMOR_PATH, "r", encoding="utf-8-sig") as file:
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
async def send_prompt_to_ollama(prompt: str, model: str = "tinyllama", temperature: float = 1.0) -> str:
    url = f"{OLLAMA_HOST}/v1/completions"
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logging.error(f"Ollama API responded {resp.status}: {text}")
                    return "❌ Ollama‑Fehler."
                data = await resp.json()

        # **Hier** den komplette Roh‑JSON loggen:
        logging.debug(f"Ollama‑Raw JSON: {json.dumps(data, ensure_ascii=False, indent=2)}")

        # OpenAI‑Style parsing…
        if "choices" in data and data["choices"]:
            choice = data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"].strip()
            if "completion" in choice:
                return choice["completion"].strip()
            if "text" in choice:
                return choice["text"].strip()

        if "completions" in data and data["completions"]:
            return data["completions"][0].get("content", "").strip()

        logging.error(f"Unexpected Ollama response shape: {data}")
        return "❌ Ungültige Antwort von Ollama."

    except Exception as e:
        logging.error(f"Ollama Fehler: {e}")
        return "❌ Fehler bei der Ollama‑Anfrage."

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
    try:
        while True:
            asyncio.run(main())  # Analysiert und sendet
            logging.info("Warte 120 Sekunden bis zur nächsten Analyse...")
            import time
            time.sleep(120)
    except KeyboardInterrupt:
        logging.info("Beendet durch Benutzer")

