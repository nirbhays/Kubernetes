# CLAUDE.md — nirbhays/Kubernetes

## Repository Purpose

Personal Kubernetes study notes and YAML manifests built while preparing for the **CKAD (Certified Kubernetes Application Developer)** exam. The CKAD is now earned — valid through September 2026.

## Owner Context

- **Name:** Nirbhay Singh
- **Background:** 11+ years cloud architecture (GCP, AWS, Azure)
- **Current Role:** Principal Platform Engineer at Siemens, Warsaw
- **CKAD Status:** Certified — valid through Sep 2026
- **Current Cert Goals:** GCP Professional Cloud DevOps Engineer, GCP PMLE

## Repository Structure

```
Kubernetes/
├── Basic Pod/                      # Foundational Pod + Deployment YAML
│   ├── pod.yaml                    # Minimal pod definition (empty/draft)
│   ├── nginx.yaml                  # Nginx pod example
│   └── Deployments/
│       └── my-deployment.yaml      # 4-replica frontend Deployment
├── CKAD/
│   └── Day one/
│       ├── PodswithYAML.yaml       # YAML-based pod creation practice
│       └── tst.py                  # Python helper for CKAD practice
├── Replicasets/
│   └── replicaset.yaml             # ReplicaSet manifest
└── CKAD_kubectl_commands.docx      # kubectl command cheatsheet
```

## Manifest Notes

### `Basic Pod/pod.yaml`
Appears to be an incomplete/draft manifest (empty `apiVersion` and `kind`). Good reference for remembering YAML schema skeleton.

### `Basic Pod/Deployments/my-deployment.yaml`
- Kind: Deployment, apiVersion: apps/v1
- 4 replicas, image: nginx
- Labels: `app: mywebsite`, `tier: frontend`
- Pod labels: `app: myapp` (note: different from selector — worth fixing to align)

### `CKAD/Day one/PodswithYAML.yaml`
Day 1 CKAD practice session — pod creation using YAML definitions.

## CKAD Exam Context

The CKAD is a **performance-based exam** (2 hours, 15–20 tasks in a live Kubernetes environment). No multiple choice — you must execute real kubectl commands and write real YAML.

Key domains tested:
- **Application Design** (20%): multi-container pods, init containers
- **Application Deployment** (20%): Deployments, rolling updates, Helm
- **Application Observability** (15%): probes, logging, metrics
- **Application Environment** (25%): ConfigMaps, Secrets, SecurityContexts, resource limits
- **Services & Networking** (20%): Services, NetworkPolicies, Ingress

## Essential kubectl Commands

```bash
# Exam setup aliases (run at start)
alias k=kubectl
export do="--dry-run=client -o yaml"

# Generate YAML quickly
k run nginx --image=nginx $do > pod.yaml
k create deployment myapp --image=nginx --replicas=3 $do > deploy.yaml

# Apply and verify
k apply -f pod.yaml
k get pods -o wide
k describe pod nginx
k logs nginx
k exec -it nginx -- /bin/sh

# Namespace operations
k get pods -n kube-system
k run test --image=busybox -n myns $do

# Services
k expose pod nginx --port=80 --target-port=80 --type=ClusterIP

# ConfigMaps and Secrets
k create configmap myconfig --from-literal=key=value
k create secret generic mysecret --from-literal=password=abc123

# Resource management
k top pods
k top nodes
k scale deployment myapp --replicas=5
```

## Extending This Repo

To add more study material:
1. Create a folder per topic (e.g., `ConfigMaps/`, `Services/`, `NetworkPolicy/`)
2. Add YAML manifests with comments explaining each field
3. Reference the Kubernetes docs URL in a comment for each manifest

## Related Resources

- Kubernetes docs: https://kubernetes.io/docs (allowed during CKAD exam)
- CKAD curriculum: https://github.com/cncf/curriculum
- Practice: https://killer.sh (comes with exam purchase)
