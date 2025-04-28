import openai

openai.api_key = "your_openai_api_key"

def analyze_logs():
    logs = "log data to analyze"  # Beispiel: Hier könnten Logs von GitLab oder anderen Quellen kommen
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Analysiere diese Logdaten: {logs}",
        max_tokens=150
    )
    return response.choices[0].text.strip()
