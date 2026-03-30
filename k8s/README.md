# Kubernetes Deployment: components.djust.org

## Prerequisites

- kubectl configured for your cluster
- cert-manager installed with a `letsencrypt-prod` ClusterIssuer
- nginx ingress controller
- DNS: `components.djust.org` → cluster ingress IP

## Required GitHub Secrets

Add these to https://github.com/djust-org/djust-components/settings/secrets/actions:

| Secret | Description |
|--------|-------------|
| `KUBECONFIG` | Base64-encoded kubeconfig: `cat ~/.kube/config \| base64` |
| `DJANGO_SECRET_KEY` | Django secret key (see below) |
| `DJUST_BUILD_TOKEN` | GitHub PAT with `repo` scope to clone djust for building wheel |

Generate a Django secret key:
```
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## Manual Deploy

```bash
# Set kubeconfig
export KUBECONFIG=~/.kube/config

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl create secret generic djust-components-secret \
  -n djust-components \
  --from-literal=secret-key="<your-secret-key>"

# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

## Trigger Deploy via GitHub Actions

Push a version tag:
```bash
git tag v0.3.1 && git push origin v0.3.1
```

Or use "Run workflow" in GitHub Actions UI.
