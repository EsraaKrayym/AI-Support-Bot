import subprocess, time, os, json, logging, signal

# Config aus ENV
IMAGE         = os.getenv("TRIVY_IMAGE", "myapp")
INTERVAL      = int(os.getenv("CHECK_INTERVAL", "120"))
TIMEOUT       = int(os.getenv("TRIVY_TIMEOUT", "300"))  # in Sekunden
REPORT_PATH   = os.getenv("TRIVY_REPORT_PATH", "/app/shared/trivy_output.json")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

stop = False
def on_sigint(signum, frame):
    global stop; stop = True
signal.signal(signal.SIGINT, on_sigint)

def run_trivy():
    try:
        res = subprocess.run(
            [
                "trivy", "image",
                "--format", "json",
                "--scanners", "vuln",                  # nur Vulnerability‑Scan
                "--timeout", f"{TIMEOUT}s",           # Timeout setzen
                "--cache-dir", "/root/.cache/trivy",
                IMAGE
            ],
            capture_output=True, text=True, timeout=TIMEOUT + 10
        )
    except subprocess.TimeoutExpired:
        logging.error("⏰ Trivy‑Timeout")
        return None, "🚨 Trivy‑Timeout"

    if res.returncode != 0:
        logging.error(f"❌ Trivy‑Error: {res.stderr.strip()}")
        return None, f"🚨 Trivy‑Error: {res.stderr.strip()}"

    # Roh‑JSON in Shared‑Volume schreiben
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(res.stdout)
    return res.stdout, None
last_seen = set()
def check_and_log():
    raw, err = run_trivy()
    if err:
        print(err)
        return

    data = json.loads(raw)
    current = {
        f"{v['VulnerabilityID']} [{v['Severity']}]: {v['Title']}"
        for entry in data.get("Results", []) for v in entry.get("Vulnerabilities", [])
    }

    new = current - last_seen
    if new:
        print("⚠️ Neue Sicherheitslücken:")
        for line in sorted(new):
            print(" • " + line)
    else:
        print("✅ Keine neuen Lücken.")
    last_seen.clear()
    last_seen.update(current)

if __name__ == "__main__":
    logging.info(f"Starte Security‑Checks für '{IMAGE}' alle {INTERVAL}s.")
    while not stop:
        check_and_log()
        time.sleep(INTERVAL)
    logging.info("Gestoppt per SIGINT")
