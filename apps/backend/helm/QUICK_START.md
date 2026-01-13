# Kubernetes Deployment Quick Start

## Simplest Method (Recommended)

### Step 1: Create Secret

```bash
# Create all secrets with one command (replace with your actual values)
kubectl create secret generic backend-secrets \
  --from-literal=OPENAI_API_KEY='sk-your-openai-key-here' \
  --from-literal=MONGODB_URI='mongodb+srv://user:pass@cluster.mongodb.net/' \
  --from-literal=ADMIN_API_KEY='your-admin-key-here'
```

**Generate ADMIN_API_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 2: Verify Secret

```bash
kubectl get secret backend-secrets
```

### Step 3: Deploy Application

```bash
# Execute in apps/backend/helm directory
helm upgrade --install backend . \
  --set image.repository=your-registry/backend \
  --set image.tag=latest
```

### Step 4: Check Deployment Status

```bash
# View pods
kubectl get pods -l app=backend

# View logs (should see "[OK] MongoDB connected successfully")
kubectl logs -l app=backend --tail=50
```

---

## Local Development (Using .env File)

```bash
# 1. Create .env file
cp .env.example .env

# 2. Edit .env and fill in your API keys

# 3. Start service
npx nx serve backend
```

---

## Update Secrets

```bash
# Delete old secret
kubectl delete secret backend-secrets

# Create new secret
kubectl create secret generic backend-secrets \
  --from-literal=OPENAI_API_KEY='new-key' \
  --from-literal=MONGODB_URI='new-uri' \
  --from-literal=ADMIN_API_KEY='new-admin-key'

# Restart deployment
kubectl rollout restart deployment backend
```

---

## Troubleshooting

### Check Why Pod Cannot Start
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Verify Secret is Correct
```bash
kubectl get secret backend-secrets -o yaml
```

### Test if Application is Working
```bash
# Port-forward to local
kubectl port-forward service/backend 8000:8000

# Test health check
curl http://localhost:8000/
```

---

## Detailed Documentation

For more advanced options and security best practices, refer to:
- [K8S_SECRETS_GUIDE.md](./K8S_SECRETS_GUIDE.md) - Complete Secrets management guide
- [secrets.example.yaml](./secrets.example.yaml) - Secret YAML example
