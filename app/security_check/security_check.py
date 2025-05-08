import subprocess
import time

def check_security():
    result = subprocess.run(['trivy', 'image', 'myapp'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')

    if "Vulnerabilities" in output:
        return output
    else:
        return "Keine Sicherheitslücken gefunden."

if __name__ == "__main__":
    while True:
        print(check_security())
        time.sleep(120)
