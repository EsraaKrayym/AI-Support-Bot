import requests
from ai_analysis import analyze_logs
from security_check import check_security

# Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1366482373914398731/lStRdbpV6aRgnYrO01o1EXpTnY4h_7JQEGdPdTZUNlQrJdNwlv5ZUB7uvUzyPeqJTJmR"

# Funktion zum Senden von Nachrichten an Discord via Webhook
def send_discord_alert(message):
    data = {
        "content": message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Fehler beim Senden der Nachricht: {response.status_code}")
    else:
        print("Nachricht erfolgreich gesendet.")

# Hauptlogik für die Analyse und das Senden von Alarme
def main():
    # Log-Analyse durchführen
    logs = analyze_logs()
    if logs:
        message = f"Fehler gefunden: {logs}"
        send_discord_alert(message)

    # Sicherheitsanalyse durchführen
    security_issues = check_security()
    if security_issues:
        message = f"Sicherheitslücke gefunden: {security_issues}"
        send_discord_alert(message)

if __name__ == "__main__":
    main()
