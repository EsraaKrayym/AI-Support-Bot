# AI-Support-Bot

Ein AI-basierter Support-Bot zur Analyse von Logs und Sicherheitsproblemen – mit einem Hauch von Humor.

## Technologien

- Python 3.8+
- Docker & Docker Compose
- Kubernetes (Minikube)
- Argo CD für GitOps-Deployment
- OpenAI GPT für Log-Analyse
- Trivy für Sicherheitsscans von Docker-Images

## Lokale Entwicklung mit Docker Compose

```bash
docker-compose build
docker-compose up
```

## Deployment mit Kubernetes

```bash
minikube start

minikube image load ai-support-bot-bot:latest
minikube image load ai-support-bot-ai_analysis:latest
minikube image load ai-support-bot-security-check:latest

kubectl apply -f k8s/
kubectl get pods
kubectl port-forward service/bot-service 8000:80
```

## Argo CD GitOps Deployment

```bash
kubectl create namespace argocd

kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

kubectl port-forward svc/argocd-server -n argocd 8088:443

kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d

kubectl apply -n argocd -f argocd-app.yaml
```

## Sicherheitsscan mit Trivy

```bash
brew install aquasecurity/trivy/trivy

trivy image --severity CRITICAL --format json --output trivy_output.json ai-support-bot-bot:latest
```
Team7 :
Lama Chihabi
Esraa Krayym
Tukazban Aliyeva
Nouran Alhabash

