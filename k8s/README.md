# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying A2A agents.

## Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Container registry access
- NGINX Ingress Controller (optional, for external access)

## Quick Start

### 1. Build and Push Docker Image

```bash
# Build image
docker build -t your-registry.com/a2a-agents:1.0.0 .

# Push to registry
docker push your-registry.com/a2a-agents:1.0.0
```

### 2. Configure Secrets

Edit `k8s/secret.yaml` with your actual credentials:

```yaml
stringData:
  GRAVITEE_BASE_URL: "https://your-actual-gateway.com/llm"
  GRAVITEE_API_KEY: "your-actual-api-key"
  GRAVITEE_API_PLATFORM_KEY: "your-actual-platform-key"
```

Or create secret via kubectl:

```bash
kubectl create namespace a2a-agents

kubectl create secret generic a2a-secrets -n a2a-agents \
  --from-literal=GRAVITEE_BASE_URL=https://your-gateway.com/llm \
  --from-literal=GRAVITEE_API_KEY=your-api-key \
  --from-literal=GRAVITEE_API_PLATFORM_KEY=your-platform-key
```

### 3. Configure Image Registry

Edit `k8s/kustomization.yaml`:

```yaml
images:
  - name: a2a-agents
    newName: your-registry.com/a2a-agents
    newTag: "1.0.0"
```

### 4. Configure Ingress (Optional)

Edit `k8s/ingress.yaml` with your domain:

```yaml
rules:
  - host: agent-a.your-domain.com
  - host: agent-b.your-domain.com
```

### 5. Deploy

Using Kustomize:

```bash
kubectl apply -k k8s/
```

Or apply individually:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/agent-a-deployment.yaml
kubectl apply -f k8s/agent-b-deployment.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
```

### 6. Verify Deployment

```bash
# Check pods
kubectl get pods -n a2a-agents

# Check services
kubectl get svc -n a2a-agents

# Check logs
kubectl logs -n a2a-agents -l app=agent-a
kubectl logs -n a2a-agents -l app=agent-b

# Test health
kubectl port-forward -n a2a-agents svc/agent-a-service 8001:8001
curl http://localhost:8001/health
```

## Architecture

```
                    ┌─────────────────┐
                    │    Ingress      │
                    │  (NGINX/Traefik)│
                    └────────┬────────┘
                             │
            ┌────────────────┴────────────────┐
            │                                 │
    ┌───────▼───────┐               ┌────────▼───────┐
    │  agent-a.domain│               │  agent-b.domain│
    └───────┬───────┘               └────────┬───────┘
            │                                 │
    ┌───────▼───────┐               ┌────────▼───────┐
    │ agent-a-svc   │               │ agent-b-svc    │
    │ (ClusterIP)   │◄──────────────│ (ClusterIP)    │
    └───────┬───────┘   A2A calls   └────────┬───────┘
            │                                 │
    ┌───────▼───────┐               ┌────────▼───────┐
    │   Agent A     │               │   Agent B      │
    │  (2+ replicas)│               │  (2+ replicas) │
    └───────────────┘               └────────────────┘
```

## Configuration

### ConfigMap (configmap.yaml)

Non-sensitive configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| AGENT_A_HOST | Agent A bind host | 0.0.0.0 |
| AGENT_A_PORT | Agent A port | 8001 |
| AGENT_A_URL | Agent A service URL | http://agent-a-service:8001 |
| AGENT_B_HOST | Agent B bind host | 0.0.0.0 |
| AGENT_B_PORT | Agent B port | 8002 |
| AGENT_B_URL | Agent B service URL | http://agent-b-service:8002 |
| LLM_MODEL | LLM model identifier | demo-openai:gpt-4.1 |
| CORS_ORIGINS | Allowed CORS origins | * |

### Secret (secret.yaml)

Sensitive configuration:

| Variable | Description |
|----------|-------------|
| GRAVITEE_BASE_URL | Gravitee gateway URL |
| GRAVITEE_API_KEY | API key |
| GRAVITEE_API_PLATFORM_KEY | Platform API key |

## Scaling

Horizontal Pod Autoscaler is configured to scale based on CPU/memory:

- **Min replicas**: 2
- **Max replicas**: 10
- **CPU threshold**: 70%
- **Memory threshold**: 80%

Manual scaling:

```bash
kubectl scale deployment agent-a -n a2a-agents --replicas=5
kubectl scale deployment agent-b -n a2a-agents --replicas=5
```

## Monitoring

### Check HPA status

```bash
kubectl get hpa -n a2a-agents
```

### View resource usage

```bash
kubectl top pods -n a2a-agents
```

## Cleanup

```bash
kubectl delete -k k8s/
# or
kubectl delete namespace a2a-agents
```
