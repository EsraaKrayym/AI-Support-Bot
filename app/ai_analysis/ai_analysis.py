import os
import time
import json
import openai
from openai.error import RateLimitError
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_logs():
    trivy_path = os.getenv("TRIVY_REPORT_PATH", "/app/shared/trivy_output.json")

    try:
        with open(trivy_path, "r", encoding="utf-8-sig") as f:
            trivy_data = json.load(f)

        # Sicherheitslücken extrahieren
        vulnerabilities = []
        for result in trivy_data.get("Results", []):
            vulnerabilities.extend(result.get("Vulnerabilities", []))

        if not vulnerabilities:
            return "✅ Keine Schwachstellen gefunden."

        # Prompt aus den Vulnerabilities bauen
        vuln_text = "\n".join(
            f"- {v.get('Title', 'Kein Titel')} ({v.get('Severity', '???')}): {v.get('Description', '')}"
            for v in vulnerabilities
        )

        full_prompt = (
                "Du bist ein Log-Analyst. Analysiere folgende Sicherheitslücken:\n\n"
                + vuln_text
        )

        # Anfrage an OpenAI senden
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Du bist ein Log-Analyst."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=300
        )

        return response.choices[0].message.content.strip()

    except FileNotFoundError:
        return "❌ Datei nicht gefunden: trivy_output.json"
    except json.JSONDecodeError as e:
        return f"❌ JSON-Fehler: {e}"
    except RateLimitError:
        print("Rate limit exceeded. Retrying in 120 seconds...")
        time.sleep(120)
        return analyze_logs()
    except Exception as e:
        return f"❌ Unerwarteter Fehler: {e}"

if __name__ == "__main__":
    while True:
        print(analyze_logs())
        print("Warte 2 Minuten auf nächste Analyse...\n")
        time.sleep(120)
