# AI-Support-Bot
# AI-based Support Bot for Technical Issues

This is a bot that analyzes logs and security issues, providing alerts and solutions in a humorous way.

## Technologies

- Python 3.8+
- Docker & Kubernetes
- GitLab CI/CD
- Argo CD for deployment
- OpenAI GPT for log analysis

## Setup

1. Clone the repository
2. Build Docker containers using `docker-compose build`
3. Run with `docker-compose up`
4. Access the bot at `http://localhost:8000`

## Deployment

This project is deployed using Argo CD and Kubernetes. Please refer to the Kubernetes files in the `k8s/` directory.
 
## Argo-CD-Anwendung erstellen
kubectl apply -f argo-app.yaml
## Docker-Container bauen und starten
docker-compose build
docker-compose up
## Kubernetes-Deployment durchführen
kubectl apply -f k8s/
## contiener starten
docker-compose up

docker build -t ai-support-bot-bot:latest .
kubectl get deployment ai-analysis-service -o yaml

