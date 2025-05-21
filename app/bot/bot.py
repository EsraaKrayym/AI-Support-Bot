import logging
import json
import asyncio
import aiohttp
import os
import discord
import requests
import subprocess
import openai



from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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


# Erstelle die Intents
intents = discord.Intents.default()  # Aktiviert standardmäßig die gängigen Ereignisse
intents.messages = True  # Aktiviert das Empfangen von Nachrichten
intents.guilds = True    # Aktiviert das Empfangen von Serverereignissen


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

# Funktion zur Erstellung des humorvollen Prompts aus Logs + Witzen
def build_prompt_with_logs(logs):
    try:
        with open(MODEL_HUMOR_PATH, "r", encoding="utf-8-sig") as file:
            # Nur echte Witzzeilen verwenden (keine PARAMETER-Zeilen)
            humor_prompts = [
                line.strip()
                for line in file.readlines()
                if line.strip() and not line.strip().lower().startswith("parameter")
            ]

        output = []

        for i, log in enumerate(logs):
            title = log.get("Title", "No Title")
            desc = log.get("Description", "Keine Beschreibung")
            severity = log.get("Severity", "UNKNOWN")
            joke = humor_prompts[i % len(humor_prompts)]  # zirkulär Witze verwenden

            message = (
                f"🛡️ **Vulnerability {i+1}**: {title} (Severity: {severity})\n"
                f"📝 Beschreibung: {desc}\n"
                f"😂 Joke: {joke}\n"
                f"🔧 Empfehlung: Patch installieren oder… frag den Praktikanten, warum das noch live ist."
            )
            output.append(message)

        return "\n\n".join(output)

    except Exception as e:
        logging.error(f"Fehler beim Erstellen des Prompts: {e}")
        return ""

def analyze_logs_with_openai(logs):
    if not logs:
        return "✅ Keine neuen Sicherheitslücken gefunden."

    prompt_intro = (
        "Du bist ein sarkastischer DevSecOps-Experte. "
        "Analysiere die folgenden Sicherheitslücken aus einem Trivy-Scan "
        "und gib eine humorvolle, aber nützliche Zusammenfassung. Verwende Emojis.\n\n"
    )

    vuln_text = "\n".join(
        f"- {v.get('Title', 'Kein Titel')} (Severity: {v.get('Severity', '???')}): {v.get('Description', '')}"
        for v in logs
    )

    full_prompt = prompt_intro + vuln_text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Du bist ein humorvoller DevSecOps-Experte, der ausschließlich auf **Deutsch** antwortet. Deine Aufgabe ist es, Sicherheitslücken sarkastisch, unterhaltsam und mit Emojis zu kommentieren."},
                {"role": "user", "content": full_prompt + "\n\n⚠️ Wichtig: Antworte bitte **ausschließlich auf Deutsch** mit einem sarkastischen Ton und passenden Emojis."}

            ],
            max_tokens=800,
            temperature=1.1
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Fehler bei OpenAI-Analyse: {e}")
        return "❌ Fehler bei der OpenAI-Analyse."


# Funktion, um die Logs an Ollama zu senden
async def send_prompt_to_ollama(prompt: str, model: str = "mistral", temperature: float = 0.7) -> str:



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

async def ask_ollama(question, model="mistral", temperature=0.7):
    return await send_prompt_to_ollama(prompt=question, model=model, temperature=temperature)


# Hauptlogik
async def main():
    try:
        logs = load_trivy_logs()
        if not logs:
            logging.error("No valid logs to process.")
            return

        # Humorvoller Ollama-Text (bestehend aus Witzen)
        prompt = build_prompt_with_logs(logs)
        if not prompt:
            logging.error("Failed to build prompt.")
            return

        ollama_response = await send_prompt_to_ollama(prompt, temperature=1.1)
        final_ollama = clean_discord_message(ollama_response)
        await send_discord_message_async("🤖 **Ollama-Analyse:**\n" + final_ollama)

        # KI-Analyse mit OpenAI
        openai_response = analyze_logs_with_openai(logs)
        final_openai = clean_discord_message(openai_response)
        await send_discord_message_async("🧠 **OpenAI-Analyse:**\n" + final_openai)

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

