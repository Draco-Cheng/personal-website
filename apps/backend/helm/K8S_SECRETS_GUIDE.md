# Kubernetes Secrets Deployment Guide

This guide explains how to securely manage and deploy sensitive information (API keys, passwords, etc.) in Kubernetes.

## Method 1: Using Secret YAML Files (Recommended for Development/Testing)

### Step 1: Create Secret File

```bash
# Copy the example file
cp secrets.example.yaml secrets.yaml

# Edit the file and fill in real API keys
# Note: secrets.yaml is in .gitignore and will not be committed to Git
```

### Step 2: Deploy Secret to Kubernetes

```bash
# Deploy Secret
kubectl apply -f secrets.yaml

# Verify Secret was created
kubectl get secret backend-secrets

# View Secret keys (values will not be displayed)
kubectl describe secret backend-secrets
```

### Step 3: Deploy Application

```bash
# Deploy with Helm (Secret will be automatically referenced)
helm upgrade --install backend . \
  --set image.repository=your-registry/backend \
  --set image.tag=latest
```

---

## Method 2: Using kubectl create secret (Recommended for Production)

### Create Secret Once (No File Record)

```bash
kubectl create secret generic backend-secrets \
  --from-literal=OPENAI_API_KEY='sk-your-key' \
  --from-literal=MONGODB_URI='mongodb+srv://user:pass@cluster.mongodb.net/' \
  --from-literal=ADMIN_API_KEY='your-admin-key'
```

### Advantages
- ✅ Does not leave files containing sensitive information locally
- ✅ Suitable for CI/CD pipeline use
- ✅ Can read from environment variables

### Example: Create from Environment Variables

```bash
# Set environment variables
export OPENAI_API_KEY="sk-your-key"
export MONGODB_URI="mongodb+srv://..."
export ADMIN_API_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Create Secret
kubectl create secret generic backend-secrets \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --from-literal=MONGODB_URI="$MONGODB_URI" \
  --from-literal=ADMIN_API_KEY="$ADMIN_API_KEY"
```

---

## Method 3: Using Sealed Secrets (Recommended for GitOps)

If you use GitOps workflows (like ArgoCD, Flux), you can use **Sealed Secrets**.

### Install Sealed Secrets Controller

```bash
# Install controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Install kubeseal CLI
# macOS
brew install kubeseal

# Windows
choco install kubeseal
```

### Using Sealed Secrets

```bash
# 1. Create regular Secret
kubectl create secret generic backend-secrets \
  --from-literal=OPENAI_API_KEY='sk-your-key' \
  --from-literal=MONGODB_URI='mongodb+srv://...' \
  --from-literal=ADMIN_API_KEY='your-admin-key' \
  --dry-run=client -o yaml > secret.yaml

# 2. Encrypt to SealedSecret
kubeseal -f secret.yaml -w sealed-secret.yaml

# 3. Commit encrypted file to Git
git add sealed-secret.yaml
git commit -m "Add backend secrets"
git push

# 4. Deploy (Controller will automatically decrypt)
kubectl apply -f sealed-secret.yaml

# 5. Delete unencrypted file
rm secret.yaml
```

---

## Method 4: Using External Secret Manager (Enterprise-Grade)

Integrate external secret management services:

### AWS Secrets Manager
```bash
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets

# Create ExternalSecret resource (example)
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: backend-secrets
spec:
  secretStoreRef:
    name: aws-secrets-manager
  target:
    name: backend-secrets
  data:
  - secretKey: OPENAI_API_KEY
    remoteRef:
      key: prod/backend/openai-key
```

### Azure Key Vault, Google Secret Manager
Similar configuration, refer to [External Secrets Operator Documentation](https://external-secrets.io/)

---

## Updating Secrets

### Update Existing Secret

```bash
# Method 1: Direct edit
kubectl edit secret backend-secrets

# Method 2: Delete and recreate
kubectl delete secret backend-secrets
kubectl create secret generic backend-secrets \
  --from-literal=OPENAI_API_KEY='new-key' \
  --from-literal=MONGODB_URI='new-uri' \
  --from-literal=ADMIN_API_KEY='new-admin-key'

# Method 3: Use patch
kubectl patch secret backend-secrets -p='{"stringData":{"OPENAI_API_KEY":"new-key"}}'
```

### Restart Pods to Load New Secret

```bash
# Helm deployment will automatically restart
helm upgrade backend .

# Or manually restart
kubectl rollout restart deployment backend
```

---

## Verify Secret Injection

### Check Pod Environment Variables

```bash
# Get Pod name
kubectl get pods -l app=backend

# View environment variables (partial display)
kubectl exec -it <pod-name> -- env | grep -E "OPENAI|MONGODB|ADMIN"

# Full view (including values, use with caution!)
kubectl exec -it <pod-name> -- printenv OPENAI_API_KEY
```

### Check Pod Logs

```bash
# Check MongoDB connection status
kubectl logs <pod-name> | grep MongoDB

# Should see:
# [OK] MongoDB connected successfully
```

---

## Security Best Practices

### 1. Use RBAC to Restrict Secret Access

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["backend-secrets"]
  verbs: ["get"]
```

### 2. Enable Secret Encryption (etcd Level)

```yaml
# /etc/kubernetes/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - aescbc:
        keys:
        - name: key1
          secret: <base64-encoded-secret>
    - identity: {}
```

### 3. Use Network Policies to Restrict Pod Communication

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
```

### 4. Regularly Rotate Secrets

```bash
# Set up cron job for regular rotation reminders
# Or use automation tools like cert-manager for automatic certificate rotation
```

---

## Troubleshooting

### Secret Not Found

```bash
# Check if Secret exists
kubectl get secret backend-secrets

# Check namespace
kubectl get secret backend-secrets -n <namespace>
```

### Pod Cannot Read Secret

```bash
# Check deployment configuration
kubectl describe deployment backend

# Check Pod events
kubectl describe pod <pod-name>

# View detailed logs
kubectl logs <pod-name> --previous
```

### Secret Values Not Updated

```bash
# After updating Secret, restart Pod
kubectl rollout restart deployment backend

# Or delete Pod (will automatically recreate)
kubectl delete pod <pod-name>
```

---

## CI/CD Integration Example

### GitHub Actions

```yaml
name: Deploy to Kubernetes
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up kubectl
      uses: azure/setup-kubectl@v1

    - name: Create/Update Secret
      env:
        KUBE_CONFIG: ${{ secrets.KUBE_CONFIG }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        MONGODB_URI: ${{ secrets.MONGODB_URI }}
        ADMIN_API_KEY: ${{ secrets.ADMIN_API_KEY }}
      run: |
        echo "$KUBE_CONFIG" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

        kubectl create secret generic backend-secrets \
          --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
          --from-literal=MONGODB_URI="$MONGODB_URI" \
          --from-literal=ADMIN_API_KEY="$ADMIN_API_KEY" \
          --dry-run=client -o yaml | kubectl apply -f -

    - name: Deploy with Helm
      run: |
        helm upgrade --install backend ./apps/backend/helm
```

---

## References

- [Kubernetes Secrets Official Documentation](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets)
- [External Secrets Operator](https://external-secrets.io/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
