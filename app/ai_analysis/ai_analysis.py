import openai
import time
from openai.error import RateLimitError

openai.api_key="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"

def analyze_logs():
    logs = "log data to analyze"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Du bist ein Log-Analyst."},
                {"role": "user", "content": f"Analysiere diese Logdaten: {logs}"}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()

    except RateLimitError:
        print("Rate limit exceeded. Retrying in 60 seconds...")
        time.sleep(60)  # Warte 60 Sekunden und versuche es dann erneut
        return analyze_logs()  # Versuch es nach der Pause erneut


if __name__ == "__main__":
    print(analyze_logs())
