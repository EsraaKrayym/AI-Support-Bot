import openai

openai.api_key="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"

def analyze_logs():
    logs = "log data to analyze"  # Beispiel: Hier könnten Logs von GitLab oder anderen Quellen kommen
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Analysiere diese Logdaten: {logs}",
        max_tokens=150
    )
    return response.choices[0].text.strip()



