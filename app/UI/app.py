import gradio as gr
import asyncio
import tempfile
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.bot import load_trivy_logs, build_prompt_with_logs, send_prompt_to_ollama, clean_discord_message, ask_ollama

# --- QA-Logik ---
def qa(payload):
    question = payload.get("question", "")
    chat_history = payload.get("chat_history", [])

    try:
        question_lower = question.lower()
        if "analyse" in question_lower or "sicherheitslücke" in question_lower:
            logs = load_trivy_logs()
            if not logs:
                return {"answer": "⚠️ Keine gültigen Logs gefunden."}
            prompt = build_prompt_with_logs(logs)
            if not prompt:
                return {"answer": "❌ Prompt konnte nicht erstellt werden."}
            response = asyncio.run(send_prompt_to_ollama(prompt, temperature=1.1))
            return {"answer": clean_discord_message(response)}
        else:
            ollama_response = asyncio.run(ask_ollama(question))
            return {"answer": clean_discord_message(ollama_response)}
    except Exception as e:
        return {"answer": f"❌ Fehler: {e}"}

# --- Export Chat ---
def export_chat(history):
    chat_log = "\n".join([f"{q}\n{a}" for q, a in history])
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f:
        f.write(chat_log)
        return f.name

# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AI IT Chatbot")

    chatbot = gr.Chatbot(label="Bot-Konversation")
    msg = gr.Textbox(placeholder="Frage stellen")
    clear = gr.Button("Neuer Chat")
    export = gr.Button("📁 Chat exportieren")
    file_out = gr.File(label="📥 Download-Link", visible=False)
    state = gr.State([])
    log_stats = gr.Markdown(value="Noch keine Analyse durchgeführt.")
    reload_logs_btn = gr.Button("🔄 Trivy-Logs neu laden")
    mode_selector = gr.Radio(
        ["Trivy-Analyse", "Freie Frage an den Bot"],
        label="Modus wählen",
        value="Trivy-Analyse"
    )

    # --- Reload Funktion ---
    def reload_logs(history):
        logs = load_trivy_logs()
        prompt = build_prompt_with_logs(logs)
        response = asyncio.run(send_prompt_to_ollama(prompt, temperature=1.1))
        now = datetime.now().strftime("%H:%M")
        message = f"🕒 {now} — **Trivy Reload**: {clean_discord_message(response)}"
        history.append(("Trivy Reload", message))
        return history

    # --- User-Handler ---
    def user(user_message, history, mode):
        if mode == "Freie Frage an den Bot":
            ollama_response = asyncio.run(ask_ollama(user_message))
            now = datetime.now().strftime("%H:%M")
            user_msg = f"🕒 {now} — **Du**: {user_message}"
            bot_msg = f"🕒 {now} — **Bot**: {clean_discord_message(ollama_response)}"
            history.append((user_msg, bot_msg))
            return "", history, history, gr.update()
        else:
            response = qa({"question": user_message, "chat_history": history})
            log_count = len(load_trivy_logs())
            now = datetime.now().strftime("%H:%M")
            user_msg = f"🕒 {now} — **Du**: {user_message}"
            bot_msg = f"🕒 {now} — **Bot**: {response['answer']}"
            history.append((user_msg, bot_msg))
            return "", history, history, gr.update(value=f"🔍 {log_count} Schwachstellen erkannt")

    # --- UI Logik verbinden ---
    reload_logs_btn.click(reload_logs, [state], [chatbot])
    msg.submit(user, [msg, state, mode_selector], [msg, chatbot, state, log_stats], queue=False)
    clear.click(lambda: ([], []), None, [chatbot, state], queue=False)
    export.click(export_chat, [state], file_out).then(lambda: gr.update(visible=True), None, file_out)

# --- App starten ---
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, debug=True, share=False)
