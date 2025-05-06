import subprocess

def check_security():
    result = subprocess.run(['trivy', 'image', 'myapp'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')

    if "Vulnerabilities" in output:
        return output
    else:
        return "Keine Sicherheitslücken gefunden."
