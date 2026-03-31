# Kubernetes Study Notes & CKAD Preparation

Personal Kubernetes study notes and hands-on YAML practice materials for the **Certified Kubernetes Application Developer (CKAD)** examination.

> **Status:** CKAD Certified — valid through September 2026.

## Repository Structure

```
Kubernetes/
├── Basic Pod/                          # Core Pod and Deployment concepts
│   ├── pod.yaml                        # Minimal Pod definition
│   ├── nginx.yaml                      # Nginx Pod example
│   └── Deployments/
│       └── my-deployment.yaml          # Multi-replica Deployment manifest
├── CKAD/                               # CKAD exam-specific practice
│   └── Day one/
│       ├── PodswithYAML.yaml           # Pod creation with YAML (Day 1 practice)
│       └── tst.py                      # Python helper script for CKAD practice
├── Replicasets/
│   └── replicaset.yaml                 # ReplicaSet manifest example
└── CKAD_kubectl_commands.docx          # kubectl command cheatsheet (Word format)
```

## Topics Covered

### Basic Pod
- Pod anatomy: `apiVersion`, `kind`, `metadata`, `spec`
- Container spec: image, ports, resource limits
- Nginx deployment as a foundational example

### Deployments
- Multi-replica Deployments with `selector.matchLabels`
- Rolling update strategy
- Label-based pod selection and management

### ReplicaSets
- ReplicaSet vs Deployment tradeoffs
- Selector/template alignment requirements
- Manual scaling

### CKAD Exam Practice
- Day-by-day structured practice sessions
- Imperative `kubectl` commands for speed (exam conditions)
- YAML generation via `kubectl run --dry-run=client -o yaml`

## Key kubectl Commands

```bash
# Create pod imperatively
kubectl run nginx --image=nginx --restart=Never

# Generate YAML without applying
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml

# Apply manifests
kubectl apply -f pod.yaml

# Get pod details
kubectl describe pod nginx

# Execute into pod
kubectl exec -it nginx -- /bin/sh

# Check ReplicaSet
kubectl get rs

# Scale deployment
kubectl scale deployment frontend --replicas=6

# Get all resources
kubectl get all -n default
```

## CKAD Exam Tips

1. **Speed is key** — use imperative commands to generate YAML, then edit minimally
2. **Know your contexts** — always verify `kubectl config current-context`
3. **Aliases help** — set `alias k=kubectl` at exam start
4. **Bookmark Kubernetes docs** — docs.kubernetes.io is allowed during exam
5. **Practice namespaces** — many questions use non-default namespaces

## Prerequisites

- Kubernetes cluster (minikube, kind, or cloud provider)
- `kubectl` CLI installed and configured
- Basic understanding of containers and Docker

## Related Certifications

| Cert | Status |
|---|---|
| CKAD | Certified (valid Sep 2026) |
| GCP Professional Cloud DevOps Engineer | In Progress |
| GCP Professional ML Engineer | Study Phase |
