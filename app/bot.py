import discord
import requests
import random
from ai_analysis import analyze_logs
from security_check import check_security

# Discord Webhook URL
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1366482373914398731/lStRdbpV6aRgnYrO01o1EXpTnY4h_7JQEGdPdTZUNlQrJdNwlv5ZUB7uvUzyPeqJTJmR"


client = discord.Client()

# Humorvolle Antworten laden (Beispiel aus model_humor.txt)
def load_humor_model():
    humor_responses = [
        "Bug gefunden? Zeit für eine Comedy-Show!",
        "Warum war der Bug traurig? Weil er in einer ungesicherten Codebase lebte!",
        "Dieses Problem ist wie ein Passwort ohne Sonderzeichen – völlig unnötig!",
        "Bug entdeckt? Na, das ist wie ein Ticket für eine Comedy-Show, aber du bist der Hauptakt."
    ]
    return humor_responses

# Funktion zum Senden von Alarme an Discord via Webhook
def send_discord_alert(message):
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Nachricht erfolgreich gesendet.")
    else:
        print(f"Fehler: {response.status_code}")

# Bot-Logik
@client.event
async def on_ready():
    print(f'Bot ist eingeloggt als {client.user}')

def main():
    # Humorvolle Antworten laden
    humor_responses = load_humor_model()

    # Log-Analyse durchführen
    logs = analyze_logs("log data to analyze")  # Beispiel: Logs als Eingabe
    if logs:
        # Eine zufällige humorvolle Antwort auswählen
        message = f"Fehler gefunden: {logs}. {random.choice(humor_responses)}"
        send_discord_alert(message)

    # Sicherheitsanalyse durchführen
    security_issues = check_security("your_docker_image")
    if security_issues:
        # Eine zufällige humorvolle Antwort auswählen
        message = f"Sicherheitslücke gefunden: {security_issues}. {random.choice(humor_responses)}"
        send_discord_alert(message)

if __name__ == "__main__":
    client.run("your_discord_bot_token")
    main()
