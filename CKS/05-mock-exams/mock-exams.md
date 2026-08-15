# CKS Mock Exams — Complete Practice Set

> **4 Full Mock Exams | 67 Total Tasks | Graduated Difficulty**
> Designed for an experienced Kubernetes engineer preparing for the CKS exam.
> CKS Exam: 2 hours, 15-20 performance-based tasks, 67% passing score, Kubernetes v1.35

**How to Use These Mock Exams:**
1. Start with Mock Exam 1 (Moderate) to establish your baseline
2. Progress to Mock Exam 2 (Real Exam Difficulty) for calibration
3. Attempt Mock Exam 3 (Troubleshooting) to build speed and diagnosis skills
4. Challenge yourself with Mock Exam 4 (Harder Than Real) for confidence

**Exam Rules:**
- Set a timer for 120 minutes — strict cutoff
- Only use https://kubernetes.io/docs and https://github.com/kubernetes as references
- No notes, no other browser tabs
- Score yourself honestly using the solutions and scoring guides

---

## Mock Exam 1: Moderate Difficulty

**Duration:** 120 minutes | **Tasks:** 16 | **Total Points:** 100 | **Passing Score:** 67 points (67%)
**Difficulty:** Moderate — Good first practice exam
**Kubernetes Version:** v1.35

### Exam Environment
- Cluster `k8s-cks-master`: Single control-plane node (Ubuntu 22.04), Kubernetes v1.35
- Cluster `ck8s`: Multi-node cluster (1 control-plane + 2 workers), Kubernetes v1.35
- Cluster `k8s-cks-worker`: Worker node access for node-level tasks

**Instructions:** Complete all tasks within the allotted time. You may use https://kubernetes.io/docs and https://github.com/kubernetes during the exam.

---

### Task 1 (5 points) — Easy
**Domain:** Cluster Setup
**Context:** `kubectl config use-context k8s-cks-master`
**Cluster:** k8s-cks-master (single control-plane node)

**Task:**
A `ClusterRole` called `node-reader` already exists in the cluster. It grants `get`, `list`, and `watch` on `nodes` resources.

Create a `ClusterRoleBinding` named `node-reader-binding` that binds the existing `ClusterRole` `node-reader` to the ServiceAccount `monitoring-sa` in the namespace `monitoring`.

The ServiceAccount `monitoring-sa` already exists.

**Namespace:** monitoring

---

### Task 2 (7 points) — Medium
**Domain:** Cluster Setup
**Context:** `kubectl config use-context ck8s`
**Cluster:** ck8s (multi-node cluster)

**Task:**
Create a `NetworkPolicy` named `api-restrict` in the namespace `production` that applies to pods with the label `app: api-server`.

The policy must:
1. Allow **ingress** traffic only from pods with the label `app: frontend` in the same namespace, on port `8080/TCP`.
2. Allow **egress** traffic only to pods with the label `app: database` in the same namespace, on port `5432/TCP`.
3. Allow **egress** traffic to DNS (UDP port 53) in all namespaces so that DNS resolution continues to work.
4. Deny all other ingress and egress traffic.

**Namespace:** production

---

### Task 3 (7 points) — Medium
**Domain:** Cluster Setup
**Context:** `kubectl config use-context k8s-cks-master`
**Cluster:** k8s-cks-master (single control-plane node)

**Task:**
The kube-apiserver on the control-plane node `k8s-cks-master` is currently configured to allow anonymous authentication and has an insecure set of admission controllers.

Perform the following on the control-plane node:
1. Edit the kube-apiserver manifest to set `--anonymous-auth=false`.
2. Ensure the admission controller `NodeRestriction` is enabled in the `--enable-admission-plugins` flag. Do not remove any existing admission controllers.
3. Verify the kube-apiserver restarts successfully after your changes.

**Note:** SSH to the control-plane node with `ssh k8s-cks-master`.

---

### Task 4 (6 points) — Medium
**Domain:** Cluster Hardening
**Context:** `kubectl config use-context ck8s`
**Cluster:** ck8s (multi-node cluster)

**Task:**
A Deployment named `legacy-app` exists in the namespace `default`. It currently runs with the default ServiceAccount.

Harden this Deployment:
1. Create a new ServiceAccount called `legacy-app-sa` in the `default` namespace.
2. Update the Deployment `legacy-app` to use the new ServiceAccount `legacy-app-sa`.
3. Ensure that the ServiceAccount token is **not** automatically mounted into the pods by setting `automountServiceAccountToken: false` on the ServiceAccount.

**Namespace:** default

---

### Task 5 (7 points) — Medium
**Domain:** Cluster Hardening
**Context:** `kubectl config use-context k8s-cks-master`
**Cluster:** k8s-cks-master (single control-plane node)

**Task:**
The Kubernetes API server is currently accessible over HTTPS but the `etcd` server is configured without proper peer certificate verification.

SSH to `k8s-cks-master` and update the etcd static pod manifest to ensure:
1. `--peer-client-cert-auth=true` is set.
2. `--peer-auto-tls=false` is set (if `--peer-auto-tls` exists, change it to `false`; if it does not exist, add it explicitly).
3. Verify that etcd restarts successfully and the cluster remains functional.

**Note:** The etcd manifest is at `/etc/kubernetes/manifests/etcd.yaml`.

---

### Task 6 (5 points) — Easy
**Domain:** Cluster Hardening
**Context:** `kubectl config use-context ck8s`
**Cluster:** ck8s (multi-node cluster)

**Task:**
A ServiceAccount named `deploy-bot` exists in the namespace `ci-cd`. It currently has a `ClusterRoleBinding` called `deploy-bot-admin` that binds it to the `cluster-admin` ClusterRole.

This is a security risk. Perform the following:
1. Delete the `ClusterRoleBinding` `deploy-bot-admin`.
2. Create a new `Role` called `deploy-bot-role` in the namespace `ci-cd` that only allows `get`, `list`, `create`, and `update` on `deployments` in the `apps` API group.
3. Create a `RoleBinding` called `deploy-bot-binding` in namespace `ci-cd` that binds `deploy-bot-role` to the ServiceAccount `deploy-bot`.

**Namespace:** ci-cd

---

### Task 7 (6 points) — Medium
**Domain:** System Hardening
**Context:** `kubectl config use-context k8s-cks-worker`
**Cluster:** k8s-cks-worker (worker node)

**Task:**
SSH to the worker node `k8s-cks-worker01`. Identify all processes listening on a port that are **not** related to Kubernetes system components (`kubelet`, `kube-proxy`, `containerd`).

1. Use an appropriate command (e.g., `ss`, `netstat`) to list all listening TCP ports.
2. Identify the non-Kubernetes process(es) listening on a port.
3. Stop and disable the identified service(s) using `systemctl`.
4. Write the name(s) of the service(s) you stopped to the file `/root/non-k8s-services.txt`, one per line.

**Note:** SSH to the worker node with `ssh k8s-cks-worker01`.

---

### Task 8 (8 points) — Hard
**Domain:** System Hardening
**Context:** `kubectl config use-context ck8s`
**Cluster:** ck8s (multi-node cluster)

**Task:**
An AppArmor profile named `k8s-deny-write` must be used to restrict a pod from writing to the filesystem.

1. SSH to node `ck8s-worker01` and create an AppArmor profile at `/etc/apparmor.d/k8s-deny-write` with the following content:
   ```
   #include <tunables/global>
   profile k8s-deny-write flags=(attach_disconnected) {
     #include <abstractions/base>
     file,
     deny /** w,
   }
   ```
2. Load the profile using `apparmor_parser`.
3. Create a pod named `secure-pod` in the namespace `apparmor-test` using the image `nginx:1.25` that uses the `k8s-deny-write` AppArmor profile on its container named `nginx`.
4. Verify that the pod starts and that write operations inside the container are denied.

**Namespace:** apparmor-test

---

### Task 9 (7 points) — Medium
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context ck8s`
**Cluster:** ck8s (multi-node cluster)

**Task:**
A Deployment named `payment-service` exists in the namespace `finance`. The pods currently run as root and have several security issues.

Update the Deployment so that all containers in the pod:
1. Run as non-root user with UID `1000`.
2. Have `allowPrivilegeEscalation` set to `false`.
3. Have a `readOnlyRootFilesystem` set to `true`.
4. Drop all Linux capabilities (drop `ALL`).
5. Add back only the `NET_BIND_SERVICE` capability.

Ensure the Deployment rolls out successfully.

**Namespace:** finance

---

### Task 10 (6 points) — Medium
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context ck8s`
**Cluster:** ck8s (multi-node cluster)

**Task:**
Create a `Secret` named `db-credentials` in the namespace `backend` with the following key-value pairs:
- `DB_USER`: `admin`
- `DB_PASSWORD`: `S3cur3P@ss!`

Then, update the existing Deployment `backend-app` in the namespace `backend` to mount this secret as environment variables in the container named `app`:
- Map `DB_USER` to environment variable `DATABASE_USER`.
- Map `DB_PASSWORD` to environment variable `DATABASE_PASSWORD`.

Do **not** mount the entire secret — use individual key references.

**Namespace:** backend

---

### Task 11 (7 points) — Medium
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context k8s-cks-master`
**Cluster:** k8s-cks-master (single control-plane node)

**Task:**
Enable encryption at rest for Kubernetes `Secrets` on the cluster `k8s-cks-master`.

1. SSH to `k8s-cks-master`.
2. Create an `EncryptionConfiguration` file at `/etc/kubernetes/enc/encryption-config.yaml` that encrypts `secrets` using the `aescbc` provider with the following key:
   - Name: `key1`
   - Secret (base64-encoded): `Y2hhbmdlLW1lLXRvLWEtcmVhbC1rZXk=`
3. Configure the kube-apiserver to use this encryption configuration by adding the `--encryption-provider-config` flag pointing to your configuration file.
4. Ensure the API server restarts successfully.
5. Re-create an existing secret named `test-secret` in namespace `default` so it becomes encrypted with the new configuration.

---

### Task 12 (5 points) — Easy
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context ck8s`
**Cluster:** ck8s (multi-node cluster)

**Task:**
Use `trivy` to scan the image `nginx:1.21` for vulnerabilities.

1. Run `trivy image nginx:1.21` and save the output to `/root/nginx-scan.txt`.
2. From the scan results, identify and write down the total number of `CRITICAL` vulnerabilities to the file `/root/nginx-critical-count.txt` (just the number, e.g., `15`).
3. Update the Deployment `web-frontend` in namespace `production` to use `nginx:1.25-alpine` instead of `nginx:1.21`, which has fewer vulnerabilities.

**Namespace:** production

---

### Task 13 (7 points) — Medium
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context k8s-cks-master`
**Cluster:** k8s-cks-master (single control-plane node)

**Task:**
Ensure that only images from the trusted registries `docker.io/library/` and `gcr.io/google-containers/` are allowed in the cluster.

1. An `ImagePolicyWebhook` admission controller backend is already deployed and is accessible at `https://image-policy.default.svc:443/validate`.
2. Create or update the `ImagePolicyWebhook` admission configuration file at `/etc/kubernetes/admission/image-policy.yaml`.
3. Create or update the kubeconfig file at `/etc/kubernetes/admission/image-policy-kubeconfig.yaml` that the webhook uses to authenticate to the backend service.
4. Enable the `ImagePolicyWebhook` admission plugin in the kube-apiserver with `--admission-control-config-file` pointing to the admission configuration.
5. Set `defaultAllow: false` so that images from untrusted registries are denied by default if the webhook is unreachable.

---

### Task 14 (6 points) — Hard
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context ck8s`
**Cluster:** ck8s (multi-node cluster)

**Task:**
A Dockerfile exists at `/root/Dockerfile` on `ck8s-master01`. It contains several security issues. SSH to `ck8s-master01` and fix the Dockerfile:

1. The base image currently uses `ubuntu:latest`. Pin it to a specific version: `ubuntu:22.04`.
2. The application currently runs as root. Add instructions to create a user `appuser` with UID `1001` and switch to that user.
3. The Dockerfile currently uses `ADD` to fetch a remote archive. Replace it with `COPY` for local files (assume the archive is already downloaded as `app.tar.gz`).
4. Remove any unnecessary packages installed with `apt-get` by adding `--no-install-recommends` and ensure `apt-get clean && rm -rf /var/lib/apt/lists/*` is run.
5. Save the fixed Dockerfile in place at `/root/Dockerfile`.

---

### Task 15 (5 points) — Easy
**Domain:** Monitoring, Logging and Runtime Security
**Context:** `kubectl config use-context ck8s`
**Cluster:** ck8s (multi-node cluster)

**Task:**
A pod named `suspicious-pod` is running in namespace `monitoring`. You suspect it is behaving abnormally.

1. Check the logs of the pod `suspicious-pod` and save the output to `/root/suspicious-logs.txt`.
2. Use `kubectl exec` to check which processes are running inside the container and save the output to `/root/suspicious-processes.txt`.
3. If the pod is running any process that is not `nginx` or a standard init process, delete the pod immediately.

**Namespace:** monitoring

---

### Task 16 (6 points) — Hard
**Domain:** Monitoring, Logging and Runtime Security
**Context:** `kubectl config use-context k8s-cks-master`
**Cluster:** k8s-cks-master (single control-plane node)

**Task:**
Configure Kubernetes audit logging on the cluster `k8s-cks-master`.

1. SSH to `k8s-cks-master`.
2. Create an audit policy file at `/etc/kubernetes/audit/audit-policy.yaml` with the following rules:
   - Log all requests to `secrets` at the `Metadata` level.
   - Log all requests to `configmaps` at the `Request` level.
   - Log all requests in the `NodeRestriction` admission at the `RequestResponse` level.
   - Set a catch-all rule to log everything else at the `None` level.
3. Configure the kube-apiserver to use this audit policy with:
   - `--audit-policy-file=/etc/kubernetes/audit/audit-policy.yaml`
   - `--audit-log-path=/var/log/kubernetes/audit/audit.log`
   - `--audit-log-maxage=30`
   - `--audit-log-maxbackup=10`
   - `--audit-log-maxsize=100`
4. Ensure proper volume mounts are added for the audit policy and log directory.
5. Verify the kube-apiserver restarts and audit logs are being written.

---
---

## Mock Exam 1 — Solutions

---

### Solution 1
**ClusterRoleBinding for ServiceAccount**

```bash
kubectl config use-context k8s-cks-master

kubectl create clusterrolebinding node-reader-binding \
  --clusterrole=node-reader \
  --serviceaccount=monitoring:monitoring-sa
```

**Fast approach:** The single `kubectl create clusterrolebinding` command above is the fastest method.

**Verification:**
```bash
kubectl get clusterrolebinding node-reader-binding -o yaml
kubectl auth can-i list nodes --as=system:serviceaccount:monitoring:monitoring-sa
```

**Points breakdown:**
| Component | Points |
|---|---|
| ClusterRoleBinding created with correct name | 2 |
| Bound to correct ClusterRole `node-reader` | 1 |
| Bound to correct ServiceAccount `monitoring:monitoring-sa` | 2 |

---

### Solution 2
**NetworkPolicy for api-server pods**

```bash
kubectl config use-context ck8s
```

```yaml
# api-restrict.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-restrict
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api-server
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - protocol: TCP
          port: 5432
    - ports:
        - protocol: UDP
          port: 53
```

```bash
kubectl apply -f api-restrict.yaml
```

**Fast approach:** Write the YAML above directly using `kubectl apply -f-` with a heredoc:
```bash
cat <<EOF | kubectl apply -f-
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-restrict
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api-server
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - protocol: TCP
          port: 5432
    - ports:
        - protocol: UDP
          port: 53
EOF
```

**Verification:**
```bash
kubectl get networkpolicy api-restrict -n production -o yaml
kubectl describe networkpolicy api-restrict -n production
```

**Points breakdown:**
| Component | Points |
|---|---|
| NetworkPolicy name and namespace correct | 1 |
| Correct podSelector (app: api-server) | 1 |
| Both policyTypes declared (Ingress + Egress) | 1 |
| Ingress rule: from frontend on port 8080 | 1 |
| Egress rule: to database on port 5432 | 1 |
| Egress rule: DNS on UDP 53 | 1 |
| Denies all other traffic (implicit by declaring policyTypes) | 1 |

---

### Solution 3
**Harden kube-apiserver flags**

```bash
ssh k8s-cks-master
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

Find the `spec.containers[0].command` section and make the following changes:

1. Change or add `--anonymous-auth=false`:
```yaml
    - --anonymous-auth=false
```

2. Find `--enable-admission-plugins` and add `NodeRestriction` if not already present:
```yaml
    - --enable-admission-plugins=NodeRestriction,NamespaceLifecycle,ServiceAccount,...
```

Save the file. The kubelet will detect the change and restart the kube-apiserver pod automatically.

**Fast approach:**
```bash
ssh k8s-cks-master

# Edit the manifest
sudo sed -i 's/--anonymous-auth=true/--anonymous-auth=false/' /etc/kubernetes/manifests/kube-apiserver.yaml

# Check if NodeRestriction is already present
grep 'NodeRestriction' /etc/kubernetes/manifests/kube-apiserver.yaml

# If not present, add it to admission plugins (manual edit recommended for safety)
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

**Verification:**
```bash
# Wait for apiserver to restart
watch crictl ps | grep kube-apiserver

# Verify the flags
kubectl -n kube-system get pod kube-apiserver-k8s-cks-master -o yaml | grep -E "anonymous-auth|admission-plugins"

# Test anonymous access is denied
curl -k https://localhost:6443/api/v1/namespaces
```

**Points breakdown:**
| Component | Points |
|---|---|
| `--anonymous-auth=false` set correctly | 3 |
| `NodeRestriction` admission plugin enabled | 3 |
| API server restarts successfully | 1 |

---

### Solution 4
**ServiceAccount hardening for legacy-app**

```bash
kubectl config use-context ck8s

# Create the ServiceAccount with automountServiceAccountToken: false
cat <<EOF | kubectl apply -f-
apiVersion: v1
kind: ServiceAccount
metadata:
  name: legacy-app-sa
  namespace: default
automountServiceAccountToken: false
EOF

# Patch the Deployment to use the new ServiceAccount
kubectl -n default set serviceaccount deployment legacy-app legacy-app-sa
```

Alternatively, patch with:
```bash
kubectl -n default patch deployment legacy-app \
  -p '{"spec":{"template":{"spec":{"serviceAccountName":"legacy-app-sa"}}}}'
```

**Fast approach:** The `kubectl set serviceaccount` command is fastest for updating the Deployment. Create the SA with `kubectl create sa legacy-app-sa` and then patch its `automountServiceAccountToken`:
```bash
kubectl create sa legacy-app-sa -n default
kubectl patch sa legacy-app-sa -n default -p '{"automountServiceAccountToken": false}'
kubectl set serviceaccount deployment legacy-app legacy-app-sa -n default
```

**Verification:**
```bash
kubectl get sa legacy-app-sa -n default -o yaml
kubectl get deployment legacy-app -n default -o yaml | grep -A2 serviceAccount
kubectl get pods -n default -l app=legacy-app -o yaml | grep -A5 serviceAccount
```

**Points breakdown:**
| Component | Points |
|---|---|
| ServiceAccount `legacy-app-sa` created | 2 |
| Deployment updated to use `legacy-app-sa` | 2 |
| `automountServiceAccountToken: false` set on SA | 2 |

---

### Solution 5
**etcd peer certificate hardening**

```bash
ssh k8s-cks-master
sudo vi /etc/kubernetes/manifests/etcd.yaml
```

In the `spec.containers[0].command` section, ensure the following flags are present:

```yaml
    - --peer-client-cert-auth=true
    - --peer-auto-tls=false
```

If `--peer-auto-tls` already exists with a `true` value, change it to `false`. If it does not exist, add the line.

Save the file and exit. etcd will restart automatically via kubelet.

**Fast approach:**
```bash
ssh k8s-cks-master

# Check current etcd flags
grep -E "peer-client-cert-auth|peer-auto-tls" /etc/kubernetes/manifests/etcd.yaml

# Edit
sudo vi /etc/kubernetes/manifests/etcd.yaml
# Add/change the two flags, save and exit
```

**Verification:**
```bash
# Watch for etcd pod restart
watch crictl ps | grep etcd

# Verify the flags are set
sudo cat /etc/kubernetes/manifests/etcd.yaml | grep -E "peer-client-cert-auth|peer-auto-tls"

# Confirm cluster is healthy
kubectl get nodes
kubectl get cs
```

**Points breakdown:**
| Component | Points |
|---|---|
| `--peer-client-cert-auth=true` set | 3 |
| `--peer-auto-tls=false` set | 2 |
| etcd and cluster remain functional | 2 |

---

### Solution 6
**RBAC least privilege for deploy-bot**

```bash
kubectl config use-context ck8s

# Step 1: Delete the overprivileged ClusterRoleBinding
kubectl delete clusterrolebinding deploy-bot-admin

# Step 2: Create a Role with limited permissions
kubectl create role deploy-bot-role \
  --verb=get,list,create,update \
  --resource=deployments.apps \
  -n ci-cd

# Step 3: Create a RoleBinding
kubectl create rolebinding deploy-bot-binding \
  --role=deploy-bot-role \
  --serviceaccount=ci-cd:deploy-bot \
  -n ci-cd
```

**Fast approach:** The three imperative commands above are the fastest approach.

**Verification:**
```bash
# Confirm ClusterRoleBinding is gone
kubectl get clusterrolebinding deploy-bot-admin 2>&1

# Confirm Role and RoleBinding
kubectl get role deploy-bot-role -n ci-cd -o yaml
kubectl get rolebinding deploy-bot-binding -n ci-cd -o yaml

# Test permissions
kubectl auth can-i create deployments --as=system:serviceaccount:ci-cd:deploy-bot -n ci-cd
kubectl auth can-i delete pods --as=system:serviceaccount:ci-cd:deploy-bot -n ci-cd
```

**Points breakdown:**
| Component | Points |
|---|---|
| ClusterRoleBinding `deploy-bot-admin` deleted | 1 |
| Role created with correct verbs and resource | 2 |
| RoleBinding created binding Role to SA | 2 |

---

### Solution 7
**Identify and stop non-Kubernetes services**

```bash
ssh k8s-cks-worker01

# Step 1: List all listening TCP ports
ss -tlnp

# Step 2: Identify non-K8s services
# Look for processes that are NOT kubelet, kube-proxy, or containerd
# For example, you might find: apache2 on port 80, or sshd on port 22 (sshd is expected)
# Common exam findings: nginx, apache2, or a custom service

# Step 3: Stop and disable the service (example with apache2)
systemctl stop apache2
systemctl disable apache2

# Step 4: Record the service name
echo "apache2" > /root/non-k8s-services.txt
```

**Fast approach:**
```bash
ssh k8s-cks-worker01
ss -tlnp | grep -v -E "kubelet|kube-proxy|containerd|sshd" > /tmp/suspicious.txt
cat /tmp/suspicious.txt
# Identify the service, then:
systemctl stop <service-name> && systemctl disable <service-name>
echo "<service-name>" > /root/non-k8s-services.txt
```

**Verification:**
```bash
# Confirm the service is no longer listening
ss -tlnp | grep -v -E "kubelet|kube-proxy|containerd|sshd"

# Confirm service is disabled
systemctl is-active <service-name>
systemctl is-enabled <service-name>

# Confirm the file
cat /root/non-k8s-services.txt
```

**Points breakdown:**
| Component | Points |
|---|---|
| Correctly identified non-K8s process(es) | 2 |
| Service(s) stopped | 2 |
| Service(s) disabled | 1 |
| Service name(s) written to file | 1 |

---

### Solution 8
**AppArmor profile for pod**

```bash
# Step 1: SSH to the worker node and create the AppArmor profile
ssh ck8s-worker01

cat <<'EOF' > /etc/apparmor.d/k8s-deny-write
#include <tunables/global>
profile k8s-deny-write flags=(attach_disconnected) {
  #include <abstractions/base>
  file,
  deny /** w,
}
EOF

# Step 2: Load the profile
apparmor_parser -q /etc/apparmor.d/k8s-deny-write

# Verify profile is loaded
aa-status | grep k8s-deny-write

# Step 3: Exit back to the control plane and create the pod
exit
```

```bash
kubectl config use-context ck8s

# Create namespace if it doesn't exist
kubectl create namespace apparmor-test --dry-run=client -o yaml | kubectl apply -f-

cat <<EOF | kubectl apply -f-
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
  namespace: apparmor-test
spec:
  nodeName: ck8s-worker01
  containers:
    - name: nginx
      image: nginx:1.25
      securityContext:
        appArmorProfile:
          type: Localhost
          localhostProfile: k8s-deny-write
EOF
```

**Fast approach:** Use the Kubernetes v1.30+ native `securityContext.appArmorProfile` field (shown above) instead of the deprecated annotation method. The annotation method also works:
```yaml
metadata:
  annotations:
    container.apparmor.security.beta.kubernetes.io/nginx: localhost/k8s-deny-write
```

**Verification:**
```bash
kubectl get pod secure-pod -n apparmor-test
kubectl exec secure-pod -n apparmor-test -- touch /tmp/testfile
# Expected: "Permission denied" or "Read-only file system"
```

**Points breakdown:**
| Component | Points |
|---|---|
| AppArmor profile file created correctly | 2 |
| Profile loaded on the correct node | 2 |
| Pod created with correct AppArmor profile reference | 3 |
| Pod runs successfully on the correct node | 1 |

---

### Solution 9
**SecurityContext hardening for payment-service**

```bash
kubectl config use-context ck8s

kubectl -n finance edit deployment payment-service
```

Add/update the following in the pod spec and container spec:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: finance
spec:
  template:
    spec:
      securityContext:
        runAsUser: 1000
        runAsNonRoot: true
      containers:
        - name: <existing-container-name>
          # ... existing fields ...
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
              add:
                - NET_BIND_SERVICE
```

**Fast approach:** Use `kubectl patch`:
```bash
kubectl -n finance patch deployment payment-service --type=strategic -p '{
  "spec": {
    "template": {
      "spec": {
        "securityContext": {
          "runAsUser": 1000,
          "runAsNonRoot": true
        },
        "containers": [{
          "name": "payment",
          "securityContext": {
            "allowPrivilegeEscalation": false,
            "readOnlyRootFilesystem": true,
            "capabilities": {
              "drop": ["ALL"],
              "add": ["NET_BIND_SERVICE"]
            }
          }
        }]
      }
    }
  }
}'
```

> **Note:** You need to know the container name. Find it first with:
> ```bash
> kubectl -n finance get deployment payment-service -o jsonpath='{.spec.template.spec.containers[*].name}'
> ```

**Verification:**
```bash
kubectl -n finance rollout status deployment payment-service
kubectl -n finance get pods -l app=payment-service
kubectl -n finance get deployment payment-service -o yaml | grep -A15 securityContext
```

**Points breakdown:**
| Component | Points |
|---|---|
| `runAsUser: 1000` set | 1 |
| `allowPrivilegeEscalation: false` | 1 |
| `readOnlyRootFilesystem: true` | 1 |
| `capabilities.drop: [ALL]` | 2 |
| `capabilities.add: [NET_BIND_SERVICE]` | 1 |
| Deployment rolls out successfully | 1 |

---

### Solution 10
**Secret creation and environment variable mounting**

```bash
kubectl config use-context ck8s

# Create the secret
kubectl create secret generic db-credentials \
  --from-literal=DB_USER=admin \
  --from-literal='DB_PASSWORD=S3cur3P@ss!' \
  -n backend
```

Then edit the Deployment:
```bash
kubectl -n backend edit deployment backend-app
```

Add environment variables to the container `app`:
```yaml
      containers:
        - name: app
          # ... existing fields ...
          env:
            - name: DATABASE_USER
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: DB_USER
            - name: DATABASE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: DB_PASSWORD
```

**Fast approach:** Use `kubectl set env`:
```bash
kubectl -n backend set env deployment backend-app \
  DATABASE_USER=admin DATABASE_PASSWORD='S3cur3P@ss!'
```
> **Warning:** `kubectl set env` with literal values does NOT create from a secret reference. For the exam requirement of mounting from a secret, you must edit the Deployment YAML or use `kubectl patch`:

```bash
kubectl -n backend patch deployment backend-app --type=strategic -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "app",
          "env": [
            {
              "name": "DATABASE_USER",
              "valueFrom": {
                "secretKeyRef": {
                  "name": "db-credentials",
                  "key": "DB_USER"
                }
              }
            },
            {
              "name": "DATABASE_PASSWORD",
              "valueFrom": {
                "secretKeyRef": {
                  "name": "db-credentials",
                  "key": "DB_PASSWORD"
                }
              }
            }
          ]
        }]
      }
    }
  }
}'
```

**Verification:**
```bash
kubectl get secret db-credentials -n backend -o yaml
kubectl -n backend rollout status deployment backend-app
kubectl -n backend exec deploy/backend-app -- env | grep DATABASE
```

**Points breakdown:**
| Component | Points |
|---|---|
| Secret created with correct keys and values | 2 |
| `DATABASE_USER` mapped from `secretKeyRef` | 2 |
| `DATABASE_PASSWORD` mapped from `secretKeyRef` | 2 |

---

### Solution 11
**Encryption at rest for Secrets**

```bash
ssh k8s-cks-master

# Step 1: Create the directory
sudo mkdir -p /etc/kubernetes/enc

# Step 2: Create the EncryptionConfiguration
cat <<EOF | sudo tee /etc/kubernetes/enc/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: Y2hhbmdlLW1lLXRvLWEtcmVhbC1rZXk=
      - identity: {}
EOF

# Step 3: Update kube-apiserver manifest
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

Add the following to the kube-apiserver command:
```yaml
    - --encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml
```

Add a volume mount:
```yaml
    volumeMounts:
      - name: enc-config
        mountPath: /etc/kubernetes/enc
        readOnly: true
```

Add a volume:
```yaml
    volumes:
      - name: enc-config
        hostPath:
          path: /etc/kubernetes/enc
          type: DirectoryOrCreate
```

After the API server restarts:
```bash
# Step 5: Re-create the existing secret so it gets encrypted
kubectl get secret test-secret -n default -o yaml | kubectl replace -f-
```

**Fast approach:** The steps above are already streamlined. Key time-savers:
- Use `tee` to create the encryption config in one shot
- Use `kubectl get | kubectl replace` to re-encrypt existing secrets

**Verification:**
```bash
# Verify apiserver is running
kubectl get nodes

# Verify encryption is working by checking etcd directly
sudo ETCDCTL_API=3 etcdctl \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/secrets/default/test-secret | hexdump -C | head -20
# You should see "k8s:enc:aescbc:v1:key1" prefix instead of plaintext
```

**Points breakdown:**
| Component | Points |
|---|---|
| EncryptionConfiguration file created correctly | 2 |
| `aescbc` provider with correct key | 1 |
| kube-apiserver `--encryption-provider-config` flag added | 2 |
| Volume and volumeMount added correctly | 1 |
| Existing secret re-created/replaced to encrypt it | 1 |

---

### Solution 12
**Trivy image scanning and image update**

```bash
kubectl config use-context ck8s

# Step 1: Scan the image
trivy image nginx:1.21 > /root/nginx-scan.txt

# Step 2: Count CRITICAL vulnerabilities
trivy image nginx:1.21 --severity CRITICAL --quiet | grep "Total:" 
# Or parse from the saved output:
grep -i "CRITICAL" /root/nginx-scan.txt | tail -1
# Write just the count number
echo "15" > /root/nginx-critical-count.txt   # Replace 15 with actual count

# Step 3: Update the Deployment
kubectl -n production set image deployment/web-frontend nginx=nginx:1.25-alpine
# (adjust container name if different — check first)
kubectl -n production get deployment web-frontend -o jsonpath='{.spec.template.spec.containers[*].name}'
```

**Fast approach:**
```bash
trivy image nginx:1.21 > /root/nginx-scan.txt
trivy image nginx:1.21 -s CRITICAL -q 2>/dev/null | grep -c "CRITICAL" > /root/nginx-critical-count.txt
kubectl -n production set image deployment/web-frontend <container-name>=nginx:1.25-alpine
```

**Verification:**
```bash
cat /root/nginx-scan.txt | head -30
cat /root/nginx-critical-count.txt
kubectl -n production get deployment web-frontend -o yaml | grep image
```

**Points breakdown:**
| Component | Points |
|---|---|
| Trivy scan output saved to correct file | 2 |
| CRITICAL count correctly identified and saved | 1 |
| Deployment image updated to `nginx:1.25-alpine` | 2 |

---

### Solution 13
**ImagePolicyWebhook admission controller**

```bash
ssh k8s-cks-master

# Step 1: Create directories
sudo mkdir -p /etc/kubernetes/admission

# Step 2: Create the kubeconfig for the webhook
cat <<EOF | sudo tee /etc/kubernetes/admission/image-policy-kubeconfig.yaml
apiVersion: v1
kind: Config
clusters:
  - name: image-policy
    cluster:
      server: https://image-policy.default.svc:443/validate
      certificate-authority: /etc/kubernetes/pki/ca.crt
contexts:
  - name: image-policy
    context:
      cluster: image-policy
      user: api-server
current-context: image-policy
users:
  - name: api-server
    user:
      client-certificate: /etc/kubernetes/pki/apiserver.crt
      client-key: /etc/kubernetes/pki/apiserver.key
EOF

# Step 3: Create the admission configuration
cat <<EOF | sudo tee /etc/kubernetes/admission/image-policy.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
  - name: ImagePolicyWebhook
    configuration:
      imagePolicy:
        kubeConfigFile: /etc/kubernetes/admission/image-policy-kubeconfig.yaml
        allowTTL: 50
        denyTTL: 50
        retryBackoff: 500
        defaultAllow: false
EOF

# Step 4: Update kube-apiserver manifest
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

Add to kube-apiserver command:
```yaml
    - --enable-admission-plugins=NodeRestriction,ImagePolicyWebhook
    - --admission-control-config-file=/etc/kubernetes/admission/image-policy.yaml
```

Add volume mount:
```yaml
    volumeMounts:
      - name: admission-config
        mountPath: /etc/kubernetes/admission
        readOnly: true
```

Add volume:
```yaml
    volumes:
      - name: admission-config
        hostPath:
          path: /etc/kubernetes/admission
          type: DirectoryOrCreate
```

**Fast approach:** Use `tee` for both config files, then a single `vi` session to edit the apiserver manifest.

**Verification:**
```bash
# Wait for apiserver to restart
watch crictl ps | grep kube-apiserver

# Test with an image from an untrusted registry
kubectl run test-untrusted --image=quay.io/some/image --dry-run=server
# Expected: should be denied

# Test with a trusted image
kubectl run test-trusted --image=docker.io/library/nginx --dry-run=server
# Expected: should be allowed (assuming webhook permits it)
```

**Points breakdown:**
| Component | Points |
|---|---|
| Webhook kubeconfig file created correctly | 2 |
| Admission configuration file with `defaultAllow: false` | 2 |
| `ImagePolicyWebhook` added to admission plugins | 2 |
| Volume and volumeMount added, apiserver restarts | 1 |

---

### Solution 14
**Dockerfile security hardening**

```bash
ssh ck8s-master01
cat /root/Dockerfile   # Review current state first
```

Original (insecure) Dockerfile (example):
```dockerfile
FROM ubuntu:latest
RUN apt-get update && apt-get install -y curl wget git
ADD https://example.com/app.tar.gz /opt/
WORKDIR /opt
CMD ["./app"]
```

Fixed Dockerfile:
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -u 1001 -m appuser
COPY app.tar.gz /opt/
WORKDIR /opt
USER appuser
CMD ["./app"]
```

```bash
# Write the fixed Dockerfile
cat <<'EOF' > /root/Dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -u 1001 -m appuser
COPY app.tar.gz /opt/
WORKDIR /opt
USER appuser
CMD ["./app"]
EOF
```

**Fast approach:** Use `cat <<'EOF' >` to write the entire fixed Dockerfile in one command.

**Verification:**
```bash
cat /root/Dockerfile
# Visually check:
# ✓ Base image pinned (ubuntu:22.04)
# ✓ Non-root user created (UID 1001) and USER set
# ✓ ADD replaced with COPY
# ✓ --no-install-recommends used
# ✓ apt-get clean && rm -rf /var/lib/apt/lists/* present
```

**Points breakdown:**
| Component | Points |
|---|---|
| Base image pinned to `ubuntu:22.04` | 1 |
| Non-root user `appuser` with UID 1001 + `USER appuser` | 2 |
| `ADD` remote URL replaced with `COPY` | 1 |
| `--no-install-recommends` + cache cleanup | 1 |
| Unnecessary packages removed | 1 |

---

### Solution 15
**Investigate suspicious pod**

```bash
kubectl config use-context ck8s

# Step 1: Get the logs
kubectl logs suspicious-pod -n monitoring > /root/suspicious-logs.txt

# Step 2: Check running processes
kubectl exec suspicious-pod -n monitoring -- ps aux > /root/suspicious-processes.txt

# Step 3: Review the processes
cat /root/suspicious-processes.txt
# Look for anything that is NOT nginx master/worker or init processes
# Examples of suspicious: cryptominer, reverse shell, nc, ncat, bash scripts

# If a suspicious process is found:
kubectl delete pod suspicious-pod -n monitoring
```

**Fast approach:**
```bash
kubectl logs suspicious-pod -n monitoring > /root/suspicious-logs.txt
kubectl exec suspicious-pod -n monitoring -- ps aux | tee /root/suspicious-processes.txt
# If suspicious processes found:
kubectl delete pod suspicious-pod -n monitoring --force --grace-period=0
```

**Verification:**
```bash
cat /root/suspicious-logs.txt
cat /root/suspicious-processes.txt
kubectl get pod suspicious-pod -n monitoring
# Expected: pod deleted or "NotFound"
```

**Points breakdown:**
| Component | Points |
|---|---|
| Logs saved to correct file | 1 |
| Process list saved to correct file | 2 |
| Suspicious process correctly identified | 1 |
| Pod deleted (if warranted) | 1 |

---

### Solution 16
**Kubernetes audit logging configuration**

```bash
ssh k8s-cks-master

# Step 1: Create directories
sudo mkdir -p /etc/kubernetes/audit
sudo mkdir -p /var/log/kubernetes/audit

# Step 2: Create the audit policy
cat <<EOF | sudo tee /etc/kubernetes/audit/audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: Metadata
    resources:
      - group: ""
        resources: ["secrets"]
  - level: Request
    resources:
      - group: ""
        resources: ["configmaps"]
  - level: RequestResponse
    omitStages:
      - "RequestReceived"
    resources:
      - group: "admission.k8s.io"
        resources: ["*"]
  - level: None
EOF

# Step 3: Edit the kube-apiserver manifest
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

Add the following to the kube-apiserver command:
```yaml
    - --audit-policy-file=/etc/kubernetes/audit/audit-policy.yaml
    - --audit-log-path=/var/log/kubernetes/audit/audit.log
    - --audit-log-maxage=30
    - --audit-log-maxbackup=10
    - --audit-log-maxsize=100
```

Add volume mounts:
```yaml
    volumeMounts:
      - name: audit-policy
        mountPath: /etc/kubernetes/audit
        readOnly: true
      - name: audit-log
        mountPath: /var/log/kubernetes/audit
```

Add volumes:
```yaml
    volumes:
      - name: audit-policy
        hostPath:
          path: /etc/kubernetes/audit
          type: DirectoryOrCreate
      - name: audit-log
        hostPath:
          path: /var/log/kubernetes/audit
          type: DirectoryOrCreate
```

**Fast approach:** Prepare the audit policy with `tee`, then make all apiserver manifest changes in a single `vi` session. Remember you need both volumes and volume mounts — forgetting either will prevent the apiserver from starting.

**Verification:**
```bash
# Wait for API server restart
watch crictl ps | grep kube-apiserver

# Verify audit logs are being generated
sudo tail -f /var/log/kubernetes/audit/audit.log | head -20

# Create a secret to trigger an audit log entry
kubectl create secret generic audit-test --from-literal=key=value -n default

# Check the audit log for the event
sudo grep "audit-test" /var/log/kubernetes/audit/audit.log
```

**Points breakdown:**
| Component | Points |
|---|---|
| Audit policy file created with correct rules | 2 |
| Secrets at Metadata level | 1 |
| ConfigMaps at Request level | 1 |
| Catch-all at None level | 1 |
| kube-apiserver flags set correctly | 2 |
| Volumes and volumeMounts configured | 2 |
| API server restarts and logs are generated | 1 |

---

### Mock Exam 1 — Scoring Guide

**Total Points: 100**
**Passing Score: 67 points (67%)**

| Score Range | Interpretation |
|---|---|
| 90–100 | Excellent — You are well-prepared for the CKS exam |
| 80–89 | Strong — Minor gaps, review weak areas |
| 67–79 | Pass — You made it, but strengthen your weak domains |
| 55–66 | Near pass — Focus study on domains where you lost points |
| 40–54 | Needs work — Review all domains systematically |
| Below 40 | Significant preparation needed — Start with fundamentals |

### Domain Score Breakdown

| Domain | Tasks | Total Points | Your Score |
|---|---|---|---|
| Cluster Setup | 1, 2, 3 | 19 | ___ |
| Cluster Hardening | 4, 5, 6 | 18 | ___ |
| System Hardening | 7, 8 | 14 | ___ |
| Minimize Microservice Vulnerabilities | 9, 10, 11 | 20 | ___ |
| Supply Chain Security | 12, 13, 14 | 18 | ___ |
| Monitoring, Logging and Runtime Security | 15, 16 | 11 | ___ |

### Weak Area Analysis

| If you missed... | Focus on... |
|---|---|
| Tasks 1, 2, 3 | NetworkPolicy syntax, kube-apiserver hardening flags, RBAC bindings |
| Tasks 4, 5, 6 | ServiceAccount best practices, etcd security, least-privilege RBAC |
| Tasks 7, 8 | Linux process management, AppArmor profile creation and pod integration |
| Tasks 9, 10, 11 | SecurityContext fields, Secret management, encryption at rest configuration |
| Tasks 12, 13, 14 | Trivy usage, ImagePolicyWebhook setup, Dockerfile best practices |
| Tasks 15, 16 | Pod investigation techniques, audit logging setup with volumes |

### Time Management Tips
- Easy tasks (1, 6, 12, 15): aim for 3–5 minutes each
- Medium tasks (2, 3, 4, 5, 7, 9, 10, 13): aim for 7–9 minutes each
- Hard tasks (8, 14, 16): aim for 10–12 minutes each
- Reserve 5–10 minutes at the end for verification



---

## Mock Exam 2: Current Exam Difficulty

**Duration:** 120 minutes | **Tasks:** 17 | **Total Points:** 100 | **Passing Score:** 67 points (67%)
**Difficulty:** Matches real CKS exam — Realistic practice
**Kubernetes Version:** v1.35

### Exam Environment
- Cluster `cks-cluster1`: Production multi-node (1 control-plane + 3 workers), Kubernetes v1.35
- Cluster `cks-cluster2`: Staging cluster (1 control-plane + 1 worker), Kubernetes v1.35
- Node `cks-controlplane`: Direct SSH access to control-plane node

**Instructions:** Complete all tasks within the allotted time. You may use https://kubernetes.io/docs and https://github.com/kubernetes during the exam.

---

### Task 1 (6 points) — Medium
**Domain:** Cluster Setup
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
A CIS Benchmark audit has identified that the Kubernetes API server on `cks-cluster1` has several insecure settings. SSH into the control-plane node `cks-cluster1-cp` and fix the following issues in the API server manifest:

1. Anonymous authentication is currently enabled. Disable it.
2. The `--authorization-mode` is set to `AlwaysAllow`. Change it to `Node,RBAC`.
3. The `--insecure-port` flag is set to `8080`. Remove this flag entirely (or set it to `0` if removal causes issues).
4. The `--profiling` flag is not set. Explicitly disable profiling.

Ensure the API server restarts successfully after the changes.

---

### Task 2 (5 points) — Easy
**Domain:** Cluster Setup
**Context:** `kubectl config use-context cks-cluster2`
**Cluster:** Staging cluster (1 control-plane + 1 worker)

**Task:**
Create a NetworkPolicy named `api-restrict` in the namespace `payments`. The policy should apply to all pods with the label `app: payment-api` and:

1. Allow **ingress** traffic only from pods with the label `app: frontend` in the namespace `web` on port `8443`.
2. Allow **egress** traffic only to pods with the label `app: payment-db` in the same namespace (`payments`) on port `5432`.
3. Deny all other ingress and egress traffic.

The namespace `web` has the label `kubernetes.io/metadata.name: web`.

---

### Task 3 (7 points) — Medium
**Domain:** Cluster Hardening
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
A ServiceAccount named `deploy-bot` exists in the namespace `ci-cd`. An audit has found that it has been granted a ClusterRoleBinding named `deploy-bot-admin` that binds it to the `cluster-admin` ClusterRole. This is over-permissive.

1. Delete the existing ClusterRoleBinding `deploy-bot-admin`.
2. Create a new Role named `deploy-bot-role` in the `ci-cd` namespace that only allows the following permissions:
   - `get`, `list`, `watch`, `create`, `update`, `patch` on `deployments` (in the `apps` API group)
   - `get`, `list` on `pods` and `services` (in the core API group)
3. Create a RoleBinding named `deploy-bot-binding` in the `ci-cd` namespace that binds the `deploy-bot` ServiceAccount to the new Role.

---

### Task 4 (6 points) — Medium
**Domain:** Cluster Hardening
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
The cluster currently allows the Kubernetes API server to be accessed from any IP address. Restrict API server access by performing the following:

1. SSH into the control-plane node `cks-cluster1-cp`.
2. Edit the API server manifest to add the `--admission-control-config-file` flag pointing to `/etc/kubernetes/admission/admission-config.yaml`.
3. Create the admission configuration file at `/etc/kubernetes/admission/admission-config.yaml` that enables the `EventRateLimit` admission plugin with a configuration that limits events to 50 per second per namespace.
4. Ensure the volume and volumeMount for the admission configuration directory are present in the API server pod spec.
5. Verify the API server restarts successfully.

---

### Task 5 (7 points) — Hard
**Domain:** Cluster Hardening
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
The cluster has an existing Kubernetes audit policy file at `/etc/kubernetes/audit/policy.yaml` on the control-plane node `cks-cluster1-cp`. The current policy logs everything at the `Metadata` level, which is too verbose and is filling up disk space.

Replace the audit policy with a new one that implements the following rules (in order):

1. Do **not** log requests to the `/healthz*`, `/readyz*`, or `/livez*` endpoints.
2. Do **not** log watch requests from the `system:kube-proxy` user.
3. Log `Secret`, `ConfigMap`, and `TokenReview` resources at the `Metadata` level (do not log request or response bodies).
4. Log all resources in the `authentication.k8s.io` and `authorization.k8s.io` API groups at the `RequestResponse` level.
5. Log all other resources at the `Request` level.

Ensure the API server is configured to use this audit policy and write audit logs to `/var/log/kubernetes/audit/audit.log` with a maximum age of 30 days and maximum backups of 10. Verify the API server restarts successfully.

---

### Task 6 (5 points) — Easy
**Domain:** System Hardening
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
On the worker node `cks-cluster1-worker1`, the following security issues have been identified:

1. An unnecessary service `rsyncd` is running. Stop and disable it using `systemctl`.
2. A SUID binary `/usr/bin/find-old` has been found that should not have the SUID bit set. Remove the SUID bit from this binary.
3. The file `/etc/kubernetes/pki/ca.key` on this worker node has permissions `0644`. Change its permissions to `0600` and ensure it is owned by `root:root`.

SSH into `cks-cluster1-worker1` to complete these tasks.

---

### Task 7 (6 points) — Medium
**Domain:** System Hardening
**Context:** `kubectl config use-context cks-cluster2`
**Cluster:** Staging cluster (1 control-plane + 1 worker)

**Task:**
Create an AppArmor profile on the worker node `cks-cluster2-worker1` and apply it to a pod:

1. SSH into `cks-cluster2-worker1` and create an AppArmor profile at `/etc/apparmor.d/restricted-nginx` that:
   - Denies all file writes
   - Denies all network raw access
   - Allows file read on `/etc/nginx/**` and `/usr/share/nginx/**`
   - Allows network TCP connections
2. Load the profile using `apparmor_parser`.
3. Create a pod named `secure-nginx` in the `staging` namespace using the `nginx:1.25` image that uses this AppArmor profile. The pod should run on `cks-cluster2-worker1`.

---

### Task 8 (7 points) — Medium
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
A Deployment named `app-backend` exists in the namespace `production`. This deployment currently runs with excessive privileges. Modify the Deployment to meet the following security requirements:

1. All containers must run as non-root (UID `1000`, GID `3000`).
2. All containers must have a read-only root filesystem.
3. All containers must drop ALL Linux capabilities and add back only `NET_BIND_SERVICE`.
4. Privilege escalation must be disallowed.
5. The container needs to write to `/tmp` and `/var/cache/app` — add `emptyDir` volumes mounted at those paths.
6. The `seccompProfile` must be set to `RuntimeDefault` at the pod level.

Ensure the Deployment rolls out successfully after the changes.

---

### Task 9 (6 points) — Medium
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
Enable Pod Security Admission on the `production` namespace with the following configuration:

1. **Enforce** the `restricted` Pod Security Standard (latest version).
2. **Audit** the `restricted` Pod Security Standard (latest version).
3. **Warn** the `restricted` Pod Security Standard (latest version).

After labeling the namespace, identify any existing pods in the `production` namespace that violate the `restricted` standard. Save the names of all violating pods (one per line) to the file `/opt/cks/violating-pods.txt` on the control-plane node.

---

### Task 10 (6 points) — Medium
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context cks-cluster2`
**Cluster:** Staging cluster (1 control-plane + 1 worker)

**Task:**
Create a RuntimeClass and deploy a pod that uses it:

1. Create a RuntimeClass named `gvisor-rc` that uses the handler `runsc`.
2. Create a pod named `sandboxed-app` in the `staging` namespace with the following specifications:
   - Image: `nginx:1.25-alpine`
   - Uses the `gvisor-rc` RuntimeClass
   - Runs as non-root user (UID `65534`)
   - Has a read-only root filesystem
   - Drops ALL capabilities
   - Mounts an `emptyDir` volume at `/tmp`
3. The pod does not need to be in `Running` state (the runtime handler may not be installed), but the YAML must be correct.

---

### Task 11 (7 points) — Hard
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
Encrypt Kubernetes Secrets at rest in etcd on the `cks-cluster1` cluster:

1. SSH into the control-plane node `cks-cluster1-cp`.
2. Create an EncryptionConfiguration file at `/etc/kubernetes/enc/encryption-config.yaml` that:
   - Uses the `aescbc` provider with a key named `secret-key-1` (base64-encoded value: `dGhpcyBpcyBhIHRlc3Qga2V5IGZvciBla2V5cw==`).
   - Falls back to the `identity` provider (to allow reading existing unencrypted secrets).
3. Configure the API server to use this encryption configuration by adding the `--encryption-provider-config` flag.
4. Ensure the necessary volume and volumeMount are added to the API server pod spec.
5. After the API server restarts, re-encrypt all existing secrets in the `default` namespace by reading and replacing them.
6. Verify that a secret stored in etcd is encrypted (not stored in plaintext).

---

### Task 12 (5 points) — Easy
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
Use `trivy` (already installed on the control-plane node `cks-cluster1-cp`) to scan the following images for vulnerabilities:

1. Scan `nginx:1.21` and save only the `HIGH` and `CRITICAL` severity vulnerabilities to `/opt/cks/trivy-nginx.txt`.
2. Scan `alpine:3.16` and save only the `CRITICAL` severity vulnerabilities to `/opt/cks/trivy-alpine.txt`.
3. In the `production` namespace, a Deployment named `legacy-web` is using an image with known critical vulnerabilities. Identify the image, scan it, and update the Deployment to use `nginx:1.25-alpine` instead.

---

### Task 13 (7 points) — Medium
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
Configure an admission webhook to enforce image policies:

1. Create a namespace named `image-policy-system`.
2. A ValidatingWebhookConfiguration has already been partially created at `/opt/cks/webhook-config.yaml` on the control-plane node. Complete and apply this configuration so that:
   - It validates `CREATE` and `UPDATE` operations on `pods` in all namespaces.
   - It calls the webhook service `image-policy-webhook` in the `image-policy-system` namespace on port `443` at path `/validate`.
   - The `failurePolicy` is set to `Fail` (deny pods if the webhook is unavailable).
   - The `namespaceSelector` excludes the `kube-system` namespace using the label `kubernetes.io/metadata.name`.
   - The `caBundle` is read from the file `/opt/cks/webhook-ca.pem` (base64-encode it).
3. Apply the completed webhook configuration.

---

### Task 14 (6 points) — Medium
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context cks-cluster2`
**Cluster:** Staging cluster (1 control-plane + 1 worker)

**Task:**
Ensure that only images from trusted registries can be deployed in the `staging` namespace:

1. Create an OPA Gatekeeper `ConstraintTemplate` named `k8sallowedregistries` that checks if a container image comes from an allowed list of registries.
2. Create a `Constraint` named `allowed-registries` that uses this template and only allows images from the following registries:
   - `docker.io/library/`
   - `gcr.io/google-containers/`
   - `registry.k8s.io/`
3. Apply both to the cluster. The constraint should only apply to the `staging` namespace.
4. Test by attempting to create a pod with an image from `quay.io/` — it should be denied. Save the error message to `/opt/cks/registry-denied.txt` on the control-plane node.

---

### Task 15 (6 points) — Hard
**Domain:** Monitoring, Logging and Runtime Security
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
Falco is installed on the worker nodes of `cks-cluster1`. A suspicious process has been detected running inside a container in the `production` namespace.

1. Check Falco logs on `cks-cluster1-worker2` and identify which pod had a shell spawned inside it. Save the pod name to `/opt/cks/falco-pod.txt`.
2. Create a custom Falco rule file at `/etc/falco/rules.d/custom-rules.yaml` on `cks-cluster1-worker2` that:
   - Detects when any process reads `/etc/shadow` inside a container.
   - Has priority `WARNING`.
   - Outputs: `"Shadow file read in container (user=%user.name pod=%k8s.pod.name file=%fd.name image=%container.image.repository)"`.
   - The rule name should be `Read Shadow File in Container`.
3. Reload Falco to apply the new rule (use `systemctl` or the hot-reload endpoint).

---

### Task 16 (5 points) — Hard
**Domain:** Monitoring, Logging and Runtime Security
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
An immutability violation has been detected. A running container in the `production` namespace has had its binary modified at runtime.

1. Use `kubectl exec` to identify which pod in the `production` namespace has a process running that was **not** part of the original container image. Check all pods with the label `app: webserver`. Compare the running processes against the expected entrypoint. Save the pod name to `/opt/cks/compromised-pod.txt`.
2. Delete the compromised pod.
3. Create a NetworkPolicy named `quarantine` in the `production` namespace that:
   - Applies to all pods with the label `quarantine: "true"`.
   - Denies **all** ingress and **all** egress traffic (complete network isolation).
4. Label one of the remaining `app: webserver` pods with `quarantine: "true"` to verify the policy can be applied.

---

### Task 17 (5 points) — Hard
**Domain:** Monitoring, Logging and Runtime Security
**Context:** `kubectl config use-context cks-cluster1`
**Cluster:** Production multi-node (1 control-plane + 3 workers)

**Task:**
Configure the Kubernetes audit logging to detect specific security-relevant events and investigate existing logs:

1. On the control-plane node `cks-cluster1-cp`, examine the existing audit log at `/var/log/kubernetes/audit/audit.log`.
2. Find all audit events where a `Secret` in the `kube-system` namespace was accessed (verb: `get` or `list`) by a user other than `system:apiserver` or `system:kube-controller-manager`. Save the usernames (unique, one per line) to `/opt/cks/secret-accessors.txt`.
3. Find all audit events where someone attempted to create a pod with `privileged: true` in any namespace. Save the namespace and pod name (format: `namespace/podname`, one per line) to `/opt/cks/privileged-attempts.txt`.

---
---

## Mock Exam 2 — Solutions

---

### Solution 1
**API Server CIS Benchmark Hardening**

```bash
# SSH into the control-plane node
ssh cks-cluster1-cp

# Edit the API server manifest
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

Modify the following flags in the `spec.containers[0].command` section:

```yaml
# Change or add these flags:
    - --anonymous-auth=false
    - --authorization-mode=Node,RBAC
    - --profiling=false
# Remove the line:
#   - --insecure-port=8080
# Or change to:
    - --insecure-port=0
```

**Fast approach:** Use `sed` for in-place edits:
```bash
sudo sed -i 's/--anonymous-auth=true/--anonymous-auth=false/' /etc/kubernetes/manifests/kube-apiserver.yaml
sudo sed -i 's/--authorization-mode=AlwaysAllow/--authorization-mode=Node,RBAC/' /etc/kubernetes/manifests/kube-apiserver.yaml
sudo sed -i 's/--insecure-port=8080/--insecure-port=0/' /etc/kubernetes/manifests/kube-apiserver.yaml
# Add profiling flag (append after another flag line)
sudo sed -i '/--insecure-port/a\    - --profiling=false' /etc/kubernetes/manifests/kube-apiserver.yaml
```

**Verification:**
```bash
# Wait for API server to restart
watch crictl ps | grep kube-apiserver

# Verify the settings
kubectl -s https://localhost:6443 --insecure-skip-tls-verify=true get pods 2>&1 | grep -i anonymous
cat /etc/kubernetes/manifests/kube-apiserver.yaml | grep -E "anonymous-auth|authorization-mode|insecure-port|profiling"
```

**Points breakdown:**
- Disable anonymous auth: 1.5 points
- Fix authorization-mode to Node,RBAC: 1.5 points
- Remove/disable insecure-port: 1.5 points
- Disable profiling: 1 point
- API server restarts successfully: 0.5 points

---

### Solution 2
**NetworkPolicy for Payment API**

```bash
kubectl config use-context cks-cluster2
```

```yaml
# Save as api-restrict.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-restrict
  namespace: payments
spec:
  podSelector:
    matchLabels:
      app: payment-api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: web
          podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8443
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: payment-db
      ports:
        - protocol: TCP
          port: 5432
```

```bash
kubectl apply -f api-restrict.yaml
```

**Fast approach:**
```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-restrict
  namespace: payments
spec:
  podSelector:
    matchLabels:
      app: payment-api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: web
          podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8443
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: payment-db
      ports:
        - protocol: TCP
          port: 5432
EOF
```

**Verification:**
```bash
kubectl get networkpolicy api-restrict -n payments -o yaml
kubectl describe networkpolicy api-restrict -n payments
```

**Points breakdown:**
- Correct podSelector for payment-api: 1 point
- Correct ingress rule (namespace + pod selector + port): 2 points
- Correct egress rule (pod selector + port): 1.5 points
- Both policyTypes specified (ensuring default deny for both): 0.5 points

---

### Solution 3
**Fix Over-Permissive RBAC**

```bash
kubectl config use-context cks-cluster1

# Step 1: Delete the over-permissive ClusterRoleBinding
kubectl delete clusterrolebinding deploy-bot-admin

# Step 2: Create the restricted Role
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deploy-bot-role
  namespace: ci-cd
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch", "create", "update", "patch"]
  - apiGroups: [""]
    resources: ["pods", "services"]
    verbs: ["get", "list"]
EOF

# Step 3: Create the RoleBinding
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: deploy-bot-binding
  namespace: ci-cd
subjects:
  - kind: ServiceAccount
    name: deploy-bot
    namespace: ci-cd
roleRef:
  kind: Role
  name: deploy-bot-role
  apiGroup: rbac.authorization.k8s.io
EOF
```

**Fast approach:** Same as above — RBAC resources are concise and don't benefit much from shortcuts.

**Verification:**
```bash
# Confirm ClusterRoleBinding is gone
kubectl get clusterrolebinding deploy-bot-admin 2>&1 | grep "not found"

# Check the new Role
kubectl get role deploy-bot-role -n ci-cd -o yaml

# Check the RoleBinding
kubectl get rolebinding deploy-bot-binding -n ci-cd -o yaml

# Test access
kubectl auth can-i create deployments --as=system:serviceaccount:ci-cd:deploy-bot -n ci-cd
# Should return "yes"
kubectl auth can-i delete pods --as=system:serviceaccount:ci-cd:deploy-bot -n ci-cd
# Should return "no"
kubectl auth can-i get pods --as=system:serviceaccount:ci-cd:deploy-bot -n kube-system
# Should return "no" (Role is namespace-scoped)
```

**Points breakdown:**
- Delete ClusterRoleBinding: 1 point
- Role with correct deployment permissions (apps API group): 2 points
- Role with correct pods/services permissions (core API group): 2 points
- RoleBinding binding ServiceAccount to Role: 2 points

---

### Solution 4
**Admission Control with EventRateLimit**

```bash
ssh cks-cluster1-cp

# Step 1: Create the admission configuration directory
sudo mkdir -p /etc/kubernetes/admission

# Step 2: Create the EventRateLimit configuration
cat <<EOF | sudo tee /etc/kubernetes/admission/eventratelimit-config.yaml
apiVersion: eventratelimit.admission.k8s.io/v1alpha1
kind: Configuration
limits:
  - type: Namespace
    qps: 50
    burst: 100
    cacheSize: 2000
EOF

# Step 3: Create the admission configuration file
cat <<EOF | sudo tee /etc/kubernetes/admission/admission-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
  - name: EventRateLimit
    path: /etc/kubernetes/admission/eventratelimit-config.yaml
EOF

# Step 4: Edit the API server manifest
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

Add to the kube-apiserver command flags:
```yaml
    - --enable-admission-plugins=NodeRestriction,EventRateLimit
    - --admission-control-config-file=/etc/kubernetes/admission/admission-config.yaml
```

Add volume and volumeMount:
```yaml
    volumeMounts:
    # ... existing mounts ...
    - name: admission-config
      mountPath: /etc/kubernetes/admission
      readOnly: true
  volumes:
  # ... existing volumes ...
  - name: admission-config
    hostPath:
      path: /etc/kubernetes/admission
      type: DirectoryOrCreate
```

**Fast approach:** Use `sed` or `vi` macros to add the volume/mount entries quickly; copy from an existing mount as a template.

**Verification:**
```bash
# Wait for API server to restart
watch crictl ps | grep kube-apiserver

# Verify admission plugins
kubectl -s https://localhost:6443 --insecure-skip-tls-verify=true api-versions
ps aux | grep kube-apiserver | grep admission-control-config-file
```

**Points breakdown:**
- EventRateLimit config file correct: 1.5 points
- Admission configuration file correct: 1.5 points
- API server flag added correctly: 1 point
- Volume and volumeMount added: 1.5 points
- API server restarts successfully: 0.5 points

---

### Solution 5
**Kubernetes Audit Policy Configuration**

```bash
ssh cks-cluster1-cp

# Create the audit policy
cat <<EOF | sudo tee /etc/kubernetes/audit/policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  # Rule 1: Do not log health check endpoints
  - level: None
    nonResourceURLs:
      - "/healthz*"
      - "/readyz*"
      - "/livez*"

  # Rule 2: Do not log watch requests from kube-proxy
  - level: None
    users:
      - "system:kube-proxy"
    verbs:
      - "watch"

  # Rule 3: Log Secrets, ConfigMaps, and TokenReviews at Metadata level
  - level: Metadata
    resources:
      - group: ""
        resources: ["secrets", "configmaps"]
      - group: "authentication.k8s.io"
        resources: ["tokenreviews"]

  # Rule 4: Log authentication and authorization API groups at RequestResponse
  - level: RequestResponse
    resources:
      - group: "authentication.k8s.io"
      - group: "authorization.k8s.io"

  # Rule 5: Log everything else at Request level
  - level: Request
EOF
```

Ensure the API server manifest has these flags:
```yaml
    - --audit-policy-file=/etc/kubernetes/audit/policy.yaml
    - --audit-log-path=/var/log/kubernetes/audit/audit.log
    - --audit-log-maxage=30
    - --audit-log-maxbackup=10
```

And the corresponding volumes/mounts:
```yaml
    volumeMounts:
    - name: audit-policy
      mountPath: /etc/kubernetes/audit
      readOnly: true
    - name: audit-log
      mountPath: /var/log/kubernetes/audit
  volumes:
  - name: audit-policy
    hostPath:
      path: /etc/kubernetes/audit
      type: DirectoryOrCreate
  - name: audit-log
    hostPath:
      path: /var/log/kubernetes/audit
      type: DirectoryOrCreate
```

```bash
# Create the log directory
sudo mkdir -p /var/log/kubernetes/audit
```

**Fast approach:** If audit is already partially configured, only replace the policy file and add any missing flags/volumes.

**Verification:**
```bash
# Wait for API server restart
watch crictl ps | grep kube-apiserver

# Verify audit log is being written
sudo tail -5 /var/log/kubernetes/audit/audit.log

# Test: access a secret and verify it's logged at Metadata level
kubectl get secret -n default
sudo tail -1 /var/log/kubernetes/audit/audit.log | python3 -m json.tool | grep -E "level|verb|resource"
```

**Points breakdown:**
- Rule 1 — None level for health endpoints: 1 point
- Rule 2 — None level for kube-proxy watch: 1 point
- Rule 3 — Metadata for Secrets/ConfigMaps/TokenReviews: 1.5 points
- Rule 4 — RequestResponse for auth API groups: 1.5 points
- Rule 5 — Request for all other resources: 1 point
- API server flags and volumes correct: 1 point

---

### Solution 6
**System Hardening on Worker Node**

```bash
# SSH into the worker node
ssh cks-cluster1-worker1

# Task 1: Stop and disable rsyncd
sudo systemctl stop rsyncd
sudo systemctl disable rsyncd
# Verify
sudo systemctl status rsyncd | grep -E "Active|Loaded"

# Task 2: Remove SUID bit from /usr/bin/find-old
sudo chmod u-s /usr/bin/find-old
# Verify
ls -la /usr/bin/find-old
# Should show -rwxr-xr-x (no 's')

# Task 3: Fix permissions on ca.key
sudo chmod 0600 /etc/kubernetes/pki/ca.key
sudo chown root:root /etc/kubernetes/pki/ca.key
# Verify
ls -la /etc/kubernetes/pki/ca.key
# Should show -rw------- root root
```

**Fast approach:**
```bash
ssh cks-cluster1-worker1
sudo systemctl stop rsyncd && sudo systemctl disable rsyncd
sudo chmod u-s /usr/bin/find-old
sudo chmod 0600 /etc/kubernetes/pki/ca.key && sudo chown root:root /etc/kubernetes/pki/ca.key
```

**Verification:**
```bash
systemctl is-active rsyncd     # Should return "inactive"
systemctl is-enabled rsyncd    # Should return "disabled"
stat -c "%a %U:%G" /usr/bin/find-old    # Should show "755 root:root" (no SUID)
stat -c "%a %U:%G" /etc/kubernetes/pki/ca.key   # Should show "600 root:root"
```

**Points breakdown:**
- Stop rsyncd: 0.5 points
- Disable rsyncd: 0.5 points
- Remove SUID bit: 2 points
- Fix ca.key permissions: 1 point
- Fix ca.key ownership: 1 point

---

### Solution 7
**AppArmor Profile and Secured Pod**

```bash
# SSH into the worker node
ssh cks-cluster2-worker1

# Step 1: Create the AppArmor profile
cat <<EOF | sudo tee /etc/apparmor.d/restricted-nginx
#include <tunables/global>

profile restricted-nginx flags=(attach_disconnected) {
  #include <abstractions/base>

  # Deny all file writes
  deny /** w,

  # Deny raw network access
  deny network raw,

  # Allow reading nginx config and content
  /etc/nginx/** r,
  /usr/share/nginx/** r,

  # Allow TCP network connections
  network tcp,
}
EOF

# Step 2: Load the profile
sudo apparmor_parser -q /etc/apparmor.d/restricted-nginx

# Verify profile is loaded
sudo aa-status | grep restricted-nginx
```

```bash
# Step 3: Create the pod (from the main terminal, not the worker node SSH)
# Exit SSH first
exit

kubectl config use-context cks-cluster2

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: secure-nginx
  namespace: staging
  annotations:
    container.apparmor.security.beta.kubernetes.io/nginx: localhost/restricted-nginx
spec:
  nodeName: cks-cluster2-worker1
  containers:
    - name: nginx
      image: nginx:1.25
      ports:
        - containerPort: 80
EOF
```

> **Note:** In Kubernetes v1.30+, AppArmor may also be configurable via the `securityContext.appArmorProfile` field instead of annotations. Either approach is valid:

```yaml
    securityContext:
      appArmorProfile:
        type: Localhost
        localhostProfile: restricted-nginx
```

**Fast approach:** Same — AppArmor setup requires the profile creation on the node first, then the pod manifest.

**Verification:**
```bash
kubectl get pod secure-nginx -n staging -o yaml | grep -A2 apparmor
kubectl describe pod secure-nginx -n staging | grep -i apparmor
```

**Points breakdown:**
- AppArmor profile with correct deny rules: 2 points
- Profile loaded successfully: 1 point
- Pod created with correct AppArmor annotation/field: 2 points
- Pod scheduled on correct node: 1 point

---

### Solution 8
**Harden Deployment Security Context**

```bash
kubectl config use-context cks-cluster1

kubectl edit deployment app-backend -n production
```

Apply the following changes to the Deployment spec:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-backend
  namespace: production
spec:
  selector:
    matchLabels:
      app: app-backend
  template:
    metadata:
      labels:
        app: app-backend
    spec:
      securityContext:
        runAsUser: 1000
        runAsGroup: 3000
        fsGroup: 3000
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: backend
          image: app-backend:latest    # keep existing image
          securityContext:
            runAsNonRoot: true
            readOnlyRootFilesystem: true
            allowPrivilegeEscalation: false
            capabilities:
              drop:
                - ALL
              add:
                - NET_BIND_SERVICE
          volumeMounts:
            - name: tmp-vol
              mountPath: /tmp
            - name: cache-vol
              mountPath: /var/cache/app
      volumes:
        - name: tmp-vol
          emptyDir: {}
        - name: cache-vol
          emptyDir: {}
```

**Fast approach:** Use `kubectl edit` and add the security context fields directly; or use `kubectl patch`:
```bash
kubectl patch deployment app-backend -n production --type='json' -p='[
  {"op": "add", "path": "/spec/template/spec/securityContext", "value": {"runAsUser": 1000, "runAsGroup": 3000, "fsGroup": 3000, "seccompProfile": {"type": "RuntimeDefault"}}},
  {"op": "add", "path": "/spec/template/spec/containers/0/securityContext", "value": {"runAsNonRoot": true, "readOnlyRootFilesystem": true, "allowPrivilegeEscalation": false, "capabilities": {"drop": ["ALL"], "add": ["NET_BIND_SERVICE"]}}},
  {"op": "add", "path": "/spec/template/spec/volumes", "value": [{"name": "tmp-vol", "emptyDir": {}}, {"name": "cache-vol", "emptyDir": {}}]},
  {"op": "add", "path": "/spec/template/spec/containers/0/volumeMounts", "value": [{"name": "tmp-vol", "mountPath": "/tmp"}, {"name": "cache-vol", "mountPath": "/var/cache/app"}]}
]'
```

**Verification:**
```bash
kubectl rollout status deployment app-backend -n production
kubectl get pods -n production -l app=app-backend
kubectl get deployment app-backend -n production -o jsonpath='{.spec.template.spec.securityContext}'
kubectl get deployment app-backend -n production -o jsonpath='{.spec.template.spec.containers[0].securityContext}'
```

**Points breakdown:**
- runAsUser/runAsGroup at pod level: 1 point
- readOnlyRootFilesystem: 1 point
- Drop ALL capabilities + add NET_BIND_SERVICE: 1.5 points
- allowPrivilegeEscalation: false: 0.5 points
- emptyDir volumes for /tmp and /var/cache/app: 1.5 points
- seccompProfile RuntimeDefault at pod level: 1 point
- Deployment rolls out successfully: 0.5 points

---

### Solution 9
**Pod Security Admission on Production Namespace**

```bash
kubectl config use-context cks-cluster1

# Apply Pod Security Admission labels
kubectl label namespace production \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=latest \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/audit-version=latest \
  pod-security.kubernetes.io/warn=restricted \
  pod-security.kubernetes.io/warn-version=latest \
  --overwrite
```

**Identify violating pods:**
```bash
# The audit and warn labels will generate warnings for existing violating pods
# Check for violations by doing a dry-run label (warnings appear immediately upon labeling)
# Or check which pods don't meet the restricted standard

# Method 1: Re-apply the enforce label in dry-run mode to see warnings
kubectl label namespace production pod-security.kubernetes.io/enforce=restricted --dry-run=server --overwrite 2>&1

# Method 2: Check each pod manually
kubectl get pods -n production -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | while read pod; do
  # Check for privileged containers, running as root, missing seccomp, etc.
  violations=$(kubectl get pod "$pod" -n production -o jsonpath='{.spec.containers[*].securityContext.privileged}' 2>/dev/null)
  runAsNonRoot=$(kubectl get pod "$pod" -n production -o jsonpath='{.spec.containers[*].securityContext.runAsNonRoot}' 2>/dev/null)
  if [[ "$violations" == "true" ]] || [[ "$runAsNonRoot" != "true" ]]; then
    echo "$pod"
  fi
done

# Save violating pods
# The warnings from the label command show which pods violate
# Capture them:
ssh cks-cluster1-cp
```

```bash
# On the control-plane, run:
kubectl get pods -n production -o json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for pod in data['items']:
    name = pod['metadata']['name']
    spec = pod['spec']
    violates = False
    # Check pod-level securityContext
    psc = spec.get('securityContext', {})
    if not psc.get('runAsNonRoot', False):
        violates = True
    if psc.get('seccompProfile', {}).get('type', '') != 'RuntimeDefault':
        violates = True
    for c in spec.get('containers', []):
        csc = c.get('securityContext', {})
        if csc.get('privileged', False):
            violates = True
        if csc.get('allowPrivilegeEscalation', True):
            violates = True
        caps = csc.get('capabilities', {})
        if 'ALL' not in caps.get('drop', []):
            violates = True
    if violates:
        print(name)
" > /opt/cks/violating-pods.txt

cat /opt/cks/violating-pods.txt
```

**Fast approach:** When you label a namespace with enforce=restricted, Kubernetes will warn about existing pods that would violate. Capture those warnings:
```bash
kubectl label namespace production pod-security.kubernetes.io/enforce=restricted --dry-run=server --overwrite 2>&1 | grep -oP 'pod \K[^:]+' | sort -u > /tmp/violating.txt
# Transfer to control-plane file
ssh cks-cluster1-cp "cat > /opt/cks/violating-pods.txt" < /tmp/violating.txt
```

**Verification:**
```bash
kubectl get namespace production -o yaml | grep pod-security
cat /opt/cks/violating-pods.txt
```

**Points breakdown:**
- enforce=restricted label: 2 points
- audit=restricted label: 1 point
- warn=restricted label: 1 point
- Correct violating pods identified and saved: 2 points

---

### Solution 10
**RuntimeClass with gVisor**

```bash
kubectl config use-context cks-cluster2

# Step 1: Create the RuntimeClass
cat <<EOF | kubectl apply -f -
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor-rc
handler: runsc
EOF

# Step 2: Create the sandboxed pod
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: sandboxed-app
  namespace: staging
spec:
  runtimeClassName: gvisor-rc
  securityContext:
    runAsUser: 65534
    runAsNonRoot: true
  containers:
    - name: app
      image: nginx:1.25-alpine
      securityContext:
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
      volumeMounts:
        - name: tmp
          mountPath: /tmp
  volumes:
    - name: tmp
      emptyDir: {}
EOF
```

**Fast approach:** Same commands — RuntimeClass is a single short resource.

**Verification:**
```bash
kubectl get runtimeclass gvisor-rc
kubectl get pod sandboxed-app -n staging -o yaml | grep -A1 runtimeClassName
kubectl describe pod sandboxed-app -n staging
# Pod may be in Pending state if runsc handler is not installed — that's acceptable per the task
```

**Points breakdown:**
- RuntimeClass created with correct handler: 2 points
- Pod references RuntimeClass: 1 point
- Pod has runAsNonRoot + UID 65534: 1 point
- readOnlyRootFilesystem + drop ALL + emptyDir at /tmp: 2 points

---

### Solution 11
**Encrypt Secrets at Rest in etcd**

```bash
ssh cks-cluster1-cp

# Step 1: Create the encryption configuration directory
sudo mkdir -p /etc/kubernetes/enc

# Step 2: Create the EncryptionConfiguration
cat <<EOF | sudo tee /etc/kubernetes/enc/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: secret-key-1
              secret: dGhpcyBpcyBhIHRlc3Qga2V5IGZvciBla2V5cw==
      - identity: {}
EOF

# Step 3: Add the encryption-provider-config flag to the API server
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

Add the following flag:
```yaml
    - --encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml
```

Add volume and volumeMount:
```yaml
    volumeMounts:
    - name: enc-config
      mountPath: /etc/kubernetes/enc
      readOnly: true
  volumes:
  - name: enc-config
    hostPath:
      path: /etc/kubernetes/enc
      type: DirectoryOrCreate
```

```bash
# Wait for API server to restart
watch crictl ps | grep kube-apiserver

# Step 5: Re-encrypt all secrets in the default namespace
kubectl get secrets -n default -o json | kubectl replace -f -

# Step 6: Verify encryption in etcd
# Install etcdctl if not already available
ETCDCTL_API=3 etcdctl \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/secrets/default/$(kubectl get secrets -n default -o jsonpath='{.items[0].metadata.name}') | hexdump -C | head -20
```

The output should show `k8s:enc:aescbc:v1:secret-key-1` prefix instead of plaintext JSON.

**Fast approach:** The main bottleneck is waiting for API server restart. Have the encryption config ready before editing the manifest:
```bash
sudo mkdir -p /etc/kubernetes/enc
cat <<EOF | sudo tee /etc/kubernetes/enc/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: secret-key-1
              secret: dGhpcyBpcyBhIHRlc3Qga2V5IGZvciBla2V5cw==
      - identity: {}
EOF
# Then edit API server manifest with all changes at once
```

**Verification:**
```bash
# Verify encryption provider config is active
ps aux | grep kube-apiserver | grep encryption-provider-config

# Verify a secret is encrypted in etcd
ETCDCTL_API=3 etcdctl \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/secrets/default/default-token 2>/dev/null | grep -c "k8s:enc:aescbc"
```

**Points breakdown:**
- EncryptionConfiguration file correct format: 2 points
- aescbc provider with correct key: 1 point
- identity fallback provider included: 0.5 points
- API server flag added: 1 point
- Volume/volumeMount correct: 1 point
- Re-encrypt existing secrets: 1 point
- Verification of encrypted storage: 0.5 points

---

### Solution 12
**Trivy Image Scanning**

```bash
ssh cks-cluster1-cp

# Task 1: Scan nginx:1.21 for HIGH and CRITICAL
trivy image --severity HIGH,CRITICAL nginx:1.21 > /opt/cks/trivy-nginx.txt

# Task 2: Scan alpine:3.16 for CRITICAL only
trivy image --severity CRITICAL alpine:3.16 > /opt/cks/trivy-alpine.txt

# Task 3: Identify the vulnerable image in legacy-web deployment
exit  # back to kubectl context
kubectl config use-context cks-cluster1
kubectl get deployment legacy-web -n production -o jsonpath='{.spec.template.spec.containers[*].image}'
# Suppose it shows something like nginx:1.19

# Scan the image
ssh cks-cluster1-cp "trivy image --severity CRITICAL $(kubectl get deployment legacy-web -n production -o jsonpath='{.spec.template.spec.containers[0].image}')"

# Update the deployment to use the patched image
kubectl set image deployment/legacy-web -n production \
  $(kubectl get deployment legacy-web -n production -o jsonpath='{.spec.template.spec.containers[0].name}')=nginx:1.25-alpine
```

**Fast approach:**
```bash
ssh cks-cluster1-cp
trivy image --severity HIGH,CRITICAL nginx:1.21 > /opt/cks/trivy-nginx.txt
trivy image --severity CRITICAL alpine:3.16 > /opt/cks/trivy-alpine.txt
exit
kubectl set image deployment/legacy-web -n production \
  $(kubectl get deployment legacy-web -n production -o jsonpath='{.spec.template.spec.containers[0].name}')=nginx:1.25-alpine
```

**Verification:**
```bash
cat /opt/cks/trivy-nginx.txt | head -5
cat /opt/cks/trivy-alpine.txt | head -5
kubectl get deployment legacy-web -n production -o jsonpath='{.spec.template.spec.containers[0].image}'
# Should show nginx:1.25-alpine
kubectl rollout status deployment legacy-web -n production
```

**Points breakdown:**
- Correct trivy scan with HIGH,CRITICAL filter: 1.5 points
- Correct trivy scan with CRITICAL filter: 1 point
- Identify and update vulnerable image: 2 points
- Output saved to correct files: 0.5 points

---

### Solution 13
**ValidatingWebhookConfiguration for Image Policy**

```bash
kubectl config use-context cks-cluster1

# Step 1: Create namespace
kubectl create namespace image-policy-system

# Step 2: Base64 encode the CA bundle
ssh cks-cluster1-cp
CA_BUNDLE=$(cat /opt/cks/webhook-ca.pem | base64 -w 0)

# Step 3: Complete and apply the webhook configuration
cat <<EOF | kubectl apply -f -
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: image-policy-webhook
webhooks:
  - name: image-policy.example.com
    admissionReviewVersions: ["v1"]
    sideEffects: None
    failurePolicy: Fail
    clientConfig:
      service:
        name: image-policy-webhook
        namespace: image-policy-system
        port: 443
        path: /validate
      caBundle: ${CA_BUNDLE}
    rules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
    namespaceSelector:
      matchExpressions:
        - key: kubernetes.io/metadata.name
          operator: NotIn
          values: ["kube-system"]
EOF
```

**Fast approach:**
```bash
kubectl create namespace image-policy-system
CA=$(ssh cks-cluster1-cp "base64 -w0 /opt/cks/webhook-ca.pem")
cat <<EOF | kubectl apply -f -
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: image-policy-webhook
webhooks:
  - name: image-policy.example.com
    admissionReviewVersions: ["v1"]
    sideEffects: None
    failurePolicy: Fail
    clientConfig:
      service:
        name: image-policy-webhook
        namespace: image-policy-system
        port: 443
        path: /validate
      caBundle: $CA
    rules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
    namespaceSelector:
      matchExpressions:
        - key: kubernetes.io/metadata.name
          operator: NotIn
          values: ["kube-system"]
EOF
```

**Verification:**
```bash
kubectl get validatingwebhookconfiguration image-policy-webhook -o yaml
kubectl get namespace image-policy-system
# Test: try creating a pod (may fail if webhook service doesn't exist, but configuration should be correct)
kubectl run test-webhook --image=nginx -n default --dry-run=server 2>&1
```

**Points breakdown:**
- Namespace created: 0.5 points
- Correct rules (CREATE, UPDATE on pods): 1.5 points
- Correct clientConfig (service, port, path, caBundle): 2 points
- failurePolicy: Fail: 1 point
- namespaceSelector excluding kube-system: 1.5 points
- Applied successfully: 0.5 points

---

### Solution 14
**OPA Gatekeeper Allowed Registries**

```bash
kubectl config use-context cks-cluster2

# Step 1: Create the ConstraintTemplate
cat <<EOF | kubectl apply -f -
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8sallowedregistries
spec:
  crd:
    spec:
      names:
        kind: K8sAllowedRegistries
      validation:
        openAPIV3Schema:
          type: object
          properties:
            registries:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8sallowedregistries

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not startswith_any(container.image, input.parameters.registries)
          msg := sprintf("Container image '%v' is not from an allowed registry. Allowed: %v", [container.image, input.parameters.registries])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.initContainers[_]
          not startswith_any(container.image, input.parameters.registries)
          msg := sprintf("Init container image '%v' is not from an allowed registry. Allowed: %v", [container.image, input.parameters.registries])
        }

        startswith_any(str, prefixes) {
          prefix := prefixes[_]
          startswith(str, prefix)
        }
EOF

# Wait for template to be ready
sleep 5

# Step 2: Create the Constraint
cat <<EOF | kubectl apply -f -
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sAllowedRegistries
metadata:
  name: allowed-registries
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces: ["staging"]
  parameters:
    registries:
      - "docker.io/library/"
      - "gcr.io/google-containers/"
      - "registry.k8s.io/"
EOF

# Step 3: Test with a denied image
kubectl run test-denied --image=quay.io/testimage/nginx -n staging 2> /tmp/registry-denied.txt || true
# Copy the error to the required location
ssh cks-cluster2-cp "cat > /opt/cks/registry-denied.txt" < /tmp/registry-denied.txt
```

**Fast approach:** Same — Gatekeeper resources require careful YAML. Have the ConstraintTemplate Rego ready.

**Verification:**
```bash
kubectl get constrainttemplate k8sallowedregistries
kubectl get k8sallowedregistries allowed-registries -o yaml
# Test allowed image
kubectl run test-allowed --image=docker.io/library/nginx -n staging --dry-run=server
# Should succeed
# Test denied image
kubectl run test-denied2 --image=quay.io/something -n staging --dry-run=server 2>&1
# Should be denied
cat /opt/cks/registry-denied.txt
```

**Points breakdown:**
- ConstraintTemplate with correct Rego logic: 2.5 points
- Constraint targeting staging namespace: 1.5 points
- Correct list of allowed registries: 1 point
- Error message saved: 1 point

---

### Solution 15
**Falco Investigation and Custom Rules**

```bash
# Step 1: Check Falco logs on the worker node
ssh cks-cluster1-worker2

# Find shell spawn events
sudo cat /var/log/syslog | grep falco | grep "shell" | tail -20
# Or use journalctl:
sudo journalctl -u falco | grep -i "shell was spawned" | tail -10
# Or check the Falco output file:
sudo cat /var/log/falco/falco.log | grep "Terminal shell" | tail -10

# Extract the pod name from the log entry
# Falco log format typically: "Terminal shell in container (user=root pod=<podname> ...)"
# Save the pod name
echo "<identified-pod-name>" | sudo tee /opt/cks/falco-pod.txt
# From the Falco output, find the k8s.pod.name field
sudo grep "Terminal shell" /var/log/falco/falco.log | grep -oP 'pod=\K[^ )]+' | head -1 | sudo tee /opt/cks/falco-pod.txt
```

```bash
# Step 2: Create custom Falco rule
cat <<EOF | sudo tee /etc/falco/rules.d/custom-rules.yaml
- rule: Read Shadow File in Container
  desc: Detect reading of /etc/shadow inside a container
  condition: >
    open_read and
    container and
    fd.name = "/etc/shadow"
  output: >
    Shadow file read in container
    (user=%user.name pod=%k8s.pod.name file=%fd.name image=%container.image.repository)
  priority: WARNING
  tags: [filesystem, container]
EOF

# Step 3: Reload Falco
sudo systemctl restart falco
# Or use hot reload:
# sudo kill -SIGHUP $(pidof falco)
```

**Fast approach:**
```bash
ssh cks-cluster1-worker2
sudo grep -oP 'pod=\K[^ )]+' /var/log/falco/falco.log | head -1 > /opt/cks/falco-pod.txt
cat <<'EOF' | sudo tee /etc/falco/rules.d/custom-rules.yaml
- rule: Read Shadow File in Container
  desc: Detect reading of /etc/shadow inside a container
  condition: open_read and container and fd.name = "/etc/shadow"
  output: "Shadow file read in container (user=%user.name pod=%k8s.pod.name file=%fd.name image=%container.image.repository)"
  priority: WARNING
  tags: [filesystem, container]
EOF
sudo systemctl restart falco
```

**Verification:**
```bash
cat /opt/cks/falco-pod.txt
sudo falco --list | grep "Read Shadow"
sudo systemctl status falco | grep "active (running)"
# Test: exec into a container and read /etc/shadow, then check Falco logs
```

**Points breakdown:**
- Correctly identify pod from Falco logs: 2 points
- Pod name saved to correct file: 0.5 points
- Custom rule with correct condition (open_read, container, fd.name): 1.5 points
- Custom rule with correct output format: 1 point
- Falco reloaded successfully: 1 point

---

### Solution 16
**Investigate Compromised Pod and Quarantine**

```bash
kubectl config use-context cks-cluster1

# Step 1: Check all webserver pods for unexpected processes
for pod in $(kubectl get pods -n production -l app=webserver -o jsonpath='{.items[*].metadata.name}'); do
  echo "=== Pod: $pod ==="
  kubectl exec -n production "$pod" -- ps aux 2>/dev/null
  echo ""
done

# Compare against expected entrypoint (e.g., nginx should only show nginx master/worker)
# Look for unexpected processes like:
#   - /bin/bash, /bin/sh (interactive shell)
#   - curl, wget (download tools)
#   - nc, ncat (netcat)
#   - python, perl (scripting interpreters)
#   - Custom binaries not in original image

# Identify the compromised pod (the one with unexpected processes)
# Save the pod name
echo "<compromised-pod-name>" > /opt/cks/compromised-pod.txt
ssh cks-cluster1-cp "echo '<compromised-pod-name>' > /opt/cks/compromised-pod.txt"

# Step 2: Delete the compromised pod
kubectl delete pod <compromised-pod-name> -n production

# Step 3: Create quarantine NetworkPolicy
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: quarantine
  namespace: production
spec:
  podSelector:
    matchLabels:
      quarantine: "true"
  policyTypes:
    - Ingress
    - Egress
EOF

# Step 4: Label a webserver pod for quarantine testing
REMAINING_POD=$(kubectl get pods -n production -l app=webserver -o jsonpath='{.items[0].metadata.name}')
kubectl label pod "$REMAINING_POD" -n production quarantine=true
```

**Fast approach:**
```bash
# Quick one-liner to find suspicious processes
for pod in $(kubectl get pods -n production -l app=webserver -o name); do
  echo "--- $pod ---"
  kubectl exec -n production ${pod#pod/} -- ps aux 2>/dev/null | grep -vE "nginx|ps"
done
# The pod with extra processes is the compromised one
```

**Verification:**
```bash
cat /opt/cks/compromised-pod.txt
kubectl get pod <compromised-pod-name> -n production 2>&1 | grep "not found"  # deleted
kubectl get networkpolicy quarantine -n production -o yaml
kubectl get pods -n production -l quarantine=true  # should show labeled pod
# Test quarantine: from the quarantined pod, try to reach another pod
kubectl exec -n production $REMAINING_POD -- wget --timeout=2 http://some-service 2>&1 | grep -i "timed out"
```

**Points breakdown:**
- Identify compromised pod correctly: 1.5 points
- Delete compromised pod: 0.5 points
- Quarantine NetworkPolicy with empty ingress/egress (deny all): 2 points
- Label a pod for quarantine: 1 point

---

### Solution 17
**Audit Log Analysis**

```bash
ssh cks-cluster1-cp

# Step 1: Examine the audit log
sudo ls -la /var/log/kubernetes/audit/audit.log

# Step 2: Find Secret access events in kube-system by unauthorized users
sudo cat /var/log/kubernetes/audit/audit.log | python3 -c "
import json, sys
users = set()
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        continue
    # Check if it's a secret access in kube-system
    if event.get('objectRef', {}).get('resource') == 'secrets' and \
       event.get('objectRef', {}).get('namespace') == 'kube-system' and \
       event.get('verb') in ['get', 'list']:
        user = event.get('user', {}).get('username', '')
        if user not in ['system:apiserver', 'system:kube-controller-manager']:
            users.add(user)
for u in sorted(users):
    print(u)
" > /opt/cks/secret-accessors.txt

# Alternative using jq:
sudo cat /var/log/kubernetes/audit/audit.log | \
  jq -r 'select(.objectRef.resource == "secrets" and .objectRef.namespace == "kube-system" and (.verb == "get" or .verb == "list") and .user.username != "system:apiserver" and .user.username != "system:kube-controller-manager") | .user.username' | \
  sort -u > /opt/cks/secret-accessors.txt

# Step 3: Find privileged pod creation attempts
sudo cat /var/log/kubernetes/audit/audit.log | python3 -c "
import json, sys
results = set()
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        continue
    if event.get('verb') == 'create' and \
       event.get('objectRef', {}).get('resource') == 'pods':
        # Check request body for privileged: true
        req_obj = event.get('requestObject', {})
        if req_obj:
            spec = req_obj.get('spec', {})
            containers = spec.get('containers', []) + spec.get('initContainers', [])
            for c in containers:
                sc = c.get('securityContext', {})
                if sc.get('privileged') == True:
                    ns = event.get('objectRef', {}).get('namespace', 'unknown')
                    name = event.get('objectRef', {}).get('name', req_obj.get('metadata', {}).get('name', 'unknown'))
                    results.add(f'{ns}/{name}')
for r in sorted(results):
    print(r)
" > /opt/cks/privileged-attempts.txt

# Alternative with jq:
sudo cat /var/log/kubernetes/audit/audit.log | \
  jq -r 'select(.verb == "create" and .objectRef.resource == "pods" and (.requestObject.spec.containers[]?.securityContext.privileged == true)) | "\(.objectRef.namespace)/\(.objectRef.name // .requestObject.metadata.name)"' 2>/dev/null | \
  sort -u > /opt/cks/privileged-attempts.txt
```

**Fast approach:** Use `jq` for faster parsing:
```bash
# Secret accessors
cat /var/log/kubernetes/audit/audit.log | \
  jq -r 'select(.objectRef.resource=="secrets" and .objectRef.namespace=="kube-system" and (.verb=="get" or .verb=="list") and .user.username != "system:apiserver" and .user.username != "system:kube-controller-manager") | .user.username' | sort -u > /opt/cks/secret-accessors.txt

# Privileged attempts
cat /var/log/kubernetes/audit/audit.log | \
  jq -r 'select(.verb=="create" and .objectRef.resource=="pods") | select(.requestObject.spec.containers[].securityContext.privileged==true) | "\(.objectRef.namespace)/\(.objectRef.name // .requestObject.metadata.name)"' 2>/dev/null | sort -u > /opt/cks/privileged-attempts.txt
```

**Verification:**
```bash
echo "=== Secret accessors ==="
cat /opt/cks/secret-accessors.txt
echo "=== Privileged attempts ==="
cat /opt/cks/privileged-attempts.txt
# Both files should contain at least one entry
wc -l /opt/cks/secret-accessors.txt
wc -l /opt/cks/privileged-attempts.txt
```

**Points breakdown:**
- Correct jq/python query for secret access events: 1.5 points
- Correctly excluded system:apiserver and system:kube-controller-manager: 1 point
- Output saved to correct file: 0.5 points
- Correct query for privileged pod creation attempts: 1.5 points
- Correct namespace/podname format: 0.5 points

---
---

## Mock Exam 2 — Scoring Guide

---

### Points Distribution by Task

| Task | Domain | Difficulty | Points |
|------|--------|------------|--------|
| 1 | Cluster Setup | Medium | 6 |
| 2 | Cluster Setup | Easy | 5 |
| 3 | Cluster Hardening | Medium | 7 |
| 4 | Cluster Hardening | Medium | 6 |
| 5 | Cluster Hardening | Hard | 7 |
| 6 | System Hardening | Easy | 5 |
| 7 | System Hardening | Medium | 6 |
| 8 | Minimize Microservice Vulnerabilities | Medium | 7 |
| 9 | Minimize Microservice Vulnerabilities | Medium | 6 |
| 10 | Minimize Microservice Vulnerabilities | Medium | 6 |
| 11 | Minimize Microservice Vulnerabilities | Hard | 7 |
| 12 | Supply Chain Security | Easy | 5 |
| 13 | Supply Chain Security | Medium | 7 |
| 14 | Supply Chain Security | Medium | 6 |
| 15 | Monitoring, Logging and Runtime Security | Hard | 6 |
| 16 | Monitoring, Logging and Runtime Security | Hard | 5 |
| 17 | Monitoring, Logging and Runtime Security | Hard | 5 |
| | | **Total** | **100** |

### Points by Domain

| Domain | Weight | Points | Tasks |
|--------|--------|--------|-------|
| Cluster Setup | 15% | 11 | 1, 2 |
| Cluster Hardening | 15% | 20 | 3, 4, 5 |
| System Hardening | 10% | 11 | 6, 7 |
| Minimize Microservice Vulnerabilities | 20% | 26 | 8, 9, 10, 11 |
| Supply Chain Security | 20% | 18 | 12, 13, 14 |
| Monitoring, Logging and Runtime Security | 20% | 16 | 15, 16, 17 |

### Points by Difficulty

| Difficulty | Count | Points |
|------------|-------|--------|
| Easy | 3 | 15 |
| Medium | 9 | 58 |
| Hard | 5 | 30 |

### Score Interpretation

| Score Range | Interpretation |
|-------------|----------------|
| 90-100 | Excellent — very likely to pass the real CKS exam |
| 80-89 | Strong — ready for the exam, minor gaps to address |
| 67-79 | Passing — at the threshold, strengthen weak areas |
| 55-66 | Close — focused review on 2-3 domains will get you there |
| 40-54 | Needs work — review core concepts in multiple domains |
| Below 40 | Significant preparation needed — start with fundamentals |

### Weak Area Analysis

**If you missed Tasks 1, 2:** Review Cluster Setup — focus on CIS Benchmarks and NetworkPolicy.

**If you missed Tasks 3, 4, 5:** Review Cluster Hardening — practice RBAC (Role vs. ClusterRole, RoleBinding vs. ClusterRoleBinding), admission controllers, and audit policies. Task 5 (audit policy) is one of the most frequently tested topics.

**If you missed Tasks 6, 7:** Review System Hardening — practice AppArmor profile creation and loading, SUID bit identification, and systemctl operations.

**If you missed Tasks 8, 9, 10, 11:** Review Minimize Microservice Vulnerabilities — this is the highest-weighted domain. Focus on SecurityContext fields (especially the `restricted` Pod Security Standard requirements), Pod Security Admission labels, RuntimeClass, and etcd encryption.

**If you missed Tasks 12, 13, 14:** Review Supply Chain Security — practice Trivy scanning with severity filters, ValidatingWebhookConfiguration, and OPA Gatekeeper ConstraintTemplates.

**If you missed Tasks 15, 16, 17:** Review Monitoring, Logging and Runtime Security — practice Falco rule syntax and log investigation, process analysis in containers, quarantine NetworkPolicies, and audit log parsing with jq.

### Time Management Tips

- **Easy tasks (1-3 min each):** Tasks 2, 6, 12 — do these first to bank quick points.
- **Medium tasks (5-8 min each):** Tasks 1, 3, 4, 7, 8, 9, 10, 13, 14 — core of the exam.
- **Hard tasks (8-12 min each):** Tasks 5, 11, 15, 16, 17 — budget extra time, especially for Task 5 (audit policy) and Task 11 (encryption).
- Target completing all Easy + Medium tasks first (~70 minutes), then tackle Hard tasks with remaining time (~50 minutes).
- If an API server restart fails, **do not panic**. Check `/var/log/pods/` for the kube-apiserver static pod logs.

---

## Mock Exam 3: Heavy Troubleshooting / Time Pressure

**Duration:** 120 minutes | **Tasks:** 18 | **Total Points:** 100 | **Passing Score:** 67 points (67%)
**Difficulty:** Hard — Emphasizes diagnosis under time pressure
**Kubernetes Version:** v1.35

### Exam Environment
- Cluster `attack-cluster`: Compromised cluster requiring security remediation (1 CP + 2 workers)
- Cluster `secure-cluster`: Properly configured reference cluster (1 CP + 1 worker)
- Cluster `prod-cluster`: Production workloads needing security hardening (1 CP + 3 workers)
- Node `troubleshoot-cp`: Control-plane node with configuration issues

**Instructions:** Complete all tasks within the allotted time. Many tasks involve troubleshooting — read error messages carefully. You may use https://kubernetes.io/docs and https://github.com/kubernetes during the exam.

**Time Management:** With 18 tasks in 120 minutes, you have approximately 6-7 minutes per task. Start with easy/medium tasks to bank points, then tackle hard tasks.

---

### Task 1 (5 points) — Hard
**Domain:** Cluster Setup
**Context:** `kubectl config use-context troubleshoot-cp`
**Cluster:** Control-plane node `troubleshoot-cp` — the API server is not starting after an audit policy was modified.

**Task:**
The API server on node `troubleshoot-cp` is not starting. A colleague recently tried to modify the audit policy at `/etc/kubernetes/audit/policy.yaml` but introduced a YAML syntax error. The kube-apiserver static pod is in a `CrashLoopBackOff` state.

1. SSH to node `troubleshoot-cp` using `ssh troubleshoot-cp`.
2. Identify the YAML error in the audit policy file `/etc/kubernetes/audit/policy.yaml`.
3. Fix the audit policy so it is valid YAML and the API server starts successfully.
4. Ensure the audit policy logs all requests to Secrets at the `Metadata` level in all namespaces.
5. Ensure all other requests are logged at the `RequestResponse` level.
6. Verify the API server pod comes back to a `Running` state.

---

### Task 2 (4 points) — Medium
**Domain:** Cluster Hardening
**Context:** `kubectl config use-context attack-cluster`
**Cluster:** Compromised cluster requiring remediation.

**Task:**
A ServiceAccount named `dev-deployer` in namespace `staging` has been bound to the `cluster-admin` ClusterRole. This is a security violation — this ServiceAccount should only be able to create, get, list, and delete Deployments and Services in the `staging` namespace.

1. Identify and remove the ClusterRoleBinding granting `cluster-admin` to the `dev-deployer` ServiceAccount.
2. Create a Role named `deployer-role` in namespace `staging` that allows `get`, `list`, `create`, `update`, and `delete` on `deployments` (in the `apps` API group) and `services` (in the core API group).
3. Create a RoleBinding named `deployer-binding` in namespace `staging` that binds `deployer-role` to the `dev-deployer` ServiceAccount.

---

### Task 3 (6 points) — Hard
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context prod-cluster`
**Cluster:** Production workloads needing security hardening.
**Namespace:** `payments`

**Task:**
A pod named `payment-processor` in namespace `payments` is failing to start. The logs show `Error: container has runAsNonRoot and image will run as root`. However, the Deployment manifest specifies `runAsNonRoot: true` in the Pod's securityContext.

1. Investigate why the pod is failing. The container image `internal-registry.example.com/payments:v2.4` has `USER root` in its Dockerfile.
2. Fix the Deployment `payment-processor` so the container runs as user `1000` and group `1000` without modifying the image.
3. Ensure the following securityContext settings are applied at the container level:
   - `runAsNonRoot: true`
   - `runAsUser: 1000`
   - `runAsGroup: 1000`
   - `readOnlyRootFilesystem: true`
   - `allowPrivilegeEscalation: false`
   - `capabilities.drop: ["ALL"]`
4. The application writes temporary files to `/tmp`. Add an `emptyDir` volume mounted at `/tmp` so the application can still write there despite the read-only root filesystem.
5. Verify the pod starts and is in a `Running` state.

---

### Task 4 (6 points) — Hard
**Domain:** Monitoring, Logging and Runtime Security
**Context:** `kubectl config use-context prod-cluster`
**Cluster:** Production workloads needing security hardening.

**Task:**
Falco is installed on all nodes of `prod-cluster` as a DaemonSet in the `falco-system` namespace, but it is not capturing any alerts. The Falco pods are running but their logs show `Unable to open /dev/falco0` and `Error opening device`.

1. SSH to node `prod-node01` using `ssh prod-node01`.
2. Investigate why the Falco kernel module is not loaded. Check if the module is present with `lsmod | grep falco`.
3. Load the Falco kernel module: run `falco-driver-loader` to compile and insert the kernel module.
4. Verify Falco is now detecting events. Test by running: `kubectl exec -it test-pod -n falco-system -- bash` and checking Falco logs for a "Terminal shell in container" alert.
5. Additionally, Falco rules at `/etc/falco/falco_rules.local.yaml` on `prod-node01` should include a custom rule that triggers on any process executing in containers in the `payments` namespace. Create a rule named `Process Execution in Payments Namespace` with priority `WARNING` and output `"Unexpected process in payments namespace (user=%user.name command=%proc.cmdline container=%container.name namespace=%k8s.ns.name)"`.
6. Restart the Falco service to apply the new rule.

---

### Task 5 (5 points) — Medium
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context prod-cluster`
**Cluster:** Production workloads needing security hardening.
**Namespace:** `frontend`

**Task:**
An image vulnerability scan is required for all containers running in the `frontend` namespace. Use `trivy` (already installed on node `prod-cp`) to complete the following:

1. SSH to `prod-cp` using `ssh prod-cp`.
2. Scan the image `nginx:1.23` for vulnerabilities. Save the output showing only `HIGH` and `CRITICAL` vulnerabilities to `/root/trivy-nginx-report.txt`.
3. Scan the image `node:18-alpine` for vulnerabilities. Save the output showing only `CRITICAL` vulnerabilities to `/root/trivy-node-report.txt`.
4. Identify all pods in the `frontend` namespace that are using images with CRITICAL vulnerabilities. Write the pod names (one per line) to `/root/vulnerable-pods.txt`.

---

### Task 6 (7 points) — Hard
**Domain:** Cluster Setup
**Context:** `kubectl config use-context attack-cluster`
**Cluster:** Compromised cluster requiring remediation.

**Task:**
An Ingress resource in namespace `internal` is exposing the internal dashboard service (`dashboard-svc`) to the public internet without TLS. This service should only be accessible within the cluster network.

1. Delete the existing Ingress resource named `dashboard-ingress` in namespace `internal`.
2. Create a new NetworkPolicy named `dashboard-restrict` in namespace `internal` that:
   - Applies to pods with label `app: dashboard`
   - Allows ingress traffic only from pods with label `role: admin` in namespace `internal`
   - Allows ingress traffic only on port `8443`
   - Denies all other ingress traffic
3. Modify the Service `dashboard-svc` to change its type from `LoadBalancer` to `ClusterIP`.
4. Create a new Ingress resource named `dashboard-ingress` in namespace `internal` that:
   - Routes traffic from host `dashboard.internal.local` to `dashboard-svc` on port `8443`
   - Uses TLS with the existing secret `dashboard-tls` in namespace `internal`
   - Has the annotation `nginx.ingress.kubernetes.io/auth-type: basic` with `nginx.ingress.kubernetes.io/auth-secret: dashboard-auth`

---

### Task 7 (5 points) — Medium
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context prod-cluster`
**Cluster:** Production workloads needing security hardening.

**Task:**
An admission controller webhook `image-policy-webhook` is failing, causing all pod creation to be rejected. The error message is: `failed calling webhook "validate.image-policy.io": dial tcp 10.96.45.12:443: connect: connection refused`.

1. Investigate the failing ValidatingWebhookConfiguration named `image-policy-webhook`.
2. The webhook service `image-policy-svc` in namespace `kube-system` has an incorrect `targetPort`. The webhook server inside the pod listens on port `8443`, but the Service has `targetPort: 443`. Fix the Service to point to the correct `targetPort: 8443`.
3. Verify the webhook pod `image-policy-server-0` in namespace `kube-system` is running and ready.
4. Test that pod creation works by creating a test pod: `kubectl run test-webhook --image=nginx -n default`, then delete the test pod.

---

### Task 8 (6 points) — Hard
**Domain:** System Hardening
**Context:** `kubectl config use-context secure-cluster`
**Cluster:** Properly configured reference cluster.

**Task:**
An AppArmor profile for the `nginx` container is supposed to be enforced on pods in namespace `web-prod`, but the pods are running without the profile.

1. SSH to node `secure-node01` using `ssh secure-node01`.
2. The AppArmor profile is at `/etc/apparmor.d/k8s-nginx-deny-write`. Inspect it. The profile is not loaded into the kernel. Load it using `apparmor_parser -r /etc/apparmor.d/k8s-nginx-deny-write`.
3. Verify the profile is loaded: `aa-status | grep k8s-nginx-deny-write`.
4. Edit the Deployment `nginx-secure` in namespace `web-prod` to apply the AppArmor profile `k8s-nginx-deny-write` to the `nginx` container. Use the annotation `container.apparmor.security.beta.kubernetes.io/nginx: localhost/k8s-nginx-deny-write` on the pod template.
5. Verify the new pods start successfully with the AppArmor profile enforced.
6. Test the profile works: `kubectl exec` into the nginx pod and try to write a file — it should be denied.

---

### Task 9 (6 points) — Hard
**Domain:** Cluster Hardening
**Context:** `kubectl config use-context attack-cluster`
**Cluster:** Compromised cluster requiring remediation.

**Task:**
The kubelet on node `attack-worker01` has insecure settings. You must harden the kubelet configuration.

1. SSH to `attack-worker01` using `ssh attack-worker01`.
2. Inspect the kubelet configuration at `/var/lib/kubelet/config.yaml`. Fix the following issues:
   - `anonymous.enabled` is set to `true` — change it to `false`
   - `authorization.mode` is set to `AlwaysAllow` — change it to `Webhook`
   - `readOnlyPort` is set to `10255` — change it to `0` (disabled)
   - `protectKernelDefaults` is set to `false` — change it to `true`
3. Restart the kubelet: `systemctl restart kubelet`
4. Verify the kubelet is running: `systemctl status kubelet`
5. Verify that anonymous access is denied by running from the control-plane: `curl -sk https://attack-worker01:10250/pods` — it should return `401 Unauthorized`.

---

### Task 10 (4 points) — Easy
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context prod-cluster`
**Cluster:** Production workloads needing security hardening.
**Namespace:** `backend`

**Task:**
Several pods in the `backend` namespace are using images with mutable tags (`:latest` or no tag). This is a supply chain security risk.

1. Identify all pods in the `backend` namespace that are using the `:latest` tag or have no tag specified in their image. Write the pod names (one per line) to `/root/mutable-tag-pods.txt`.
2. The Deployment `api-server` in namespace `backend` uses image `registry.example.com/api:latest`. Update it to use the image digest instead: `registry.example.com/api@sha256:a]b3c4d5e6f7890123456789abcdef0123456789abcdef0123456789abcdef01`.
3. Verify the Deployment rolls out successfully with the new image reference.

---

### Task 11 (7 points) — Hard
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context attack-cluster`
**Cluster:** Compromised cluster requiring remediation.
**Namespace:** `data-store`

**Task:**
A container in namespace `data-store` has been identified as having a privilege escalation vector through a `hostPath` volume mount. The Deployment `redis-cache` mounts `/` (the host root filesystem) at `/host` inside the container.

1. Identify the Deployment `redis-cache` in namespace `data-store` and confirm it has the dangerous `hostPath` mount.
2. Edit the Deployment to remove the `hostPath` volume and its corresponding volumeMount entirely.
3. Create a PodSecurityPolicy (or Pod Security Admission if applicable) enforcement. Label the namespace `data-store` with `pod-security.kubernetes.io/enforce: restricted` to prevent future hostPath mounts.
4. Additionally, create a NetworkPolicy named `redis-restrict` in namespace `data-store` that:
   - Applies to pods with label `app: redis`
   - Allows ingress only from pods with label `app: api` on port `6379`
   - Allows egress only to DNS (port 53 UDP/TCP) and nothing else
5. Verify the `redis-cache` pods restart without the hostPath mount and the NetworkPolicy is applied.

---

### Task 12 (6 points) — Medium
**Domain:** Monitoring, Logging and Runtime Security
**Context:** `kubectl config use-context prod-cluster`
**Cluster:** Production workloads needing security hardening.

**Task:**
The audit logging configuration on `prod-cluster` is missing events. The current audit policy at `/etc/kubernetes/audit/policy.yaml` on node `prod-cp` only logs events at the `None` level for most resources.

1. SSH to `prod-cp` using `ssh prod-cp`.
2. Modify the audit policy file `/etc/kubernetes/audit/policy.yaml` to implement these rules (in order):
   - Do not log requests to endpoints `/healthz*`, `/readyz*`, `/livez*` (level `None`)
   - Log `Secret` resources in all namespaces at `Metadata` level
   - Log `ConfigMap` resources in all namespaces at `Request` level
   - Log all resources in the `kube-system` namespace at `Metadata` level
   - Log `pods/exec`, `pods/portforward`, and `pods/attach` at `RequestResponse` level
   - Catch-all: log everything else at `Request` level
3. Ensure the kube-apiserver is configured with `--audit-log-path=/var/log/kubernetes/audit/audit.log` and `--audit-log-maxage=30` and `--audit-log-maxbackup=10` and `--audit-log-maxsize=100`.
4. Restart the API server by moving and re-placing the static pod manifest. Wait for it to come back up.
5. Verify audit logs are being written to `/var/log/kubernetes/audit/audit.log`.

---

### Task 13 (6 points) — Medium
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context prod-cluster`
**Cluster:** Production workloads needing security hardening.
**Namespace:** `secrets-app`

**Task:**
The Deployment `config-reader` in namespace `secrets-app` has Secrets mounted as environment variables, which is less secure than mounting them as files (environment variables can leak through process listings and crash dumps).

1. Identify which Secrets are being passed as environment variables in the `config-reader` Deployment in namespace `secrets-app`. The container `app` uses `envFrom` referencing `secretRef: db-credentials` and individual `env` entries referencing `secretKeyRef` from secret `api-keys`.
2. Modify the Deployment to remove all `envFrom` and `env` entries that reference Secrets.
3. Instead, mount the Secret `db-credentials` as a volume at `/etc/secrets/db` and the Secret `api-keys` as a volume at `/etc/secrets/api` — both with `defaultMode: 0400`.
4. Add an environment variable `DB_CREDENTIALS_PATH=/etc/secrets/db` and `API_KEYS_PATH=/etc/secrets/api` so the application knows where to find the files.
5. Verify the pod starts and the secrets are mounted as files with the correct permissions.

---

### Task 14 (6 points) — Hard
**Domain:** Cluster Setup
**Context:** `kubectl config use-context troubleshoot-cp`
**Cluster:** Control-plane node with configuration issues.

**Task:**
The EncryptionConfiguration for encrypting Secrets at rest in etcd has been broken. The API server logs show `error decrypting value` when trying to read existing Secrets.

1. SSH to node `troubleshoot-cp` using `ssh troubleshoot-cp`.
2. Inspect the EncryptionConfiguration at `/etc/kubernetes/enc/encryption-config.yaml`. The current config uses `aescbc` as the first provider but the encryption key has been changed, so it can no longer decrypt previously-encrypted Secrets.
3. The original encryption key is backed up at `/root/original-encryption-key.txt`. Fix the EncryptionConfiguration by adding the original key back as the second key under `aescbc` (the new key should remain as the first key so new Secrets are encrypted with it, but the old key is available for decrypting existing Secrets).
4. Restart the API server by moving the static pod manifest out of `/etc/kubernetes/manifests/` and back.
5. Verify the API server starts and existing Secrets can be read: `kubectl get secret -n default test-secret -o jsonpath='{.data.password}' | base64 -d`
6. Re-encrypt all existing Secrets with the new key: `kubectl get secrets --all-namespaces -o json | kubectl replace -f -`

---

### Task 15 (5 points) — Medium
**Domain:** Cluster Hardening
**Context:** `kubectl config use-context attack-cluster`
**Cluster:** Compromised cluster requiring remediation.

**Task:**
A CIS Kubernetes Benchmark scan has identified the following failures on node `attack-cp`. Remediate them.

1. SSH to `attack-cp` using `ssh attack-cp`.
2. Fix the following CIS benchmark failures:
   - **1.1.12:** The etcd data directory `/var/lib/etcd` has permissions `777`. Change permissions to `700` and ensure ownership is `etcd:etcd`.
   - **1.2.6:** The kube-apiserver is running without `--kubelet-certificate-authority`. Add the flag `--kubelet-certificate-authority=/etc/kubernetes/pki/ca.crt` to the kube-apiserver static pod manifest at `/etc/kubernetes/manifests/kube-apiserver.yaml`.
   - **1.2.16:** The admission controller `PodSecurity` is not enabled. Add `PodSecurity` to the `--enable-admission-plugins` flag in the kube-apiserver manifest (preserve existing admission plugins).
3. Wait for the API server to restart after manifest changes.
4. Verify the fixes: check etcd directory permissions, confirm the API server flags include the new settings.

---

### Task 16 (5 points) — Medium
**Domain:** Monitoring, Logging and Runtime Security
**Context:** `kubectl config use-context prod-cluster`
**Cluster:** Production workloads needing security hardening.
**Namespace:** `monitoring`

**Task:**
A container in the `monitoring` namespace is running as root despite a Pod Security Admission policy being set to `restricted` on the namespace. The pod `prometheus-agent-0` is somehow bypassing the policy.

1. Investigate why the pod `prometheus-agent-0` in namespace `monitoring` is running as root even though the namespace has `pod-security.kubernetes.io/enforce: restricted`.
2. Check the namespace labels: the label `pod-security.kubernetes.io/enforce` is set to `restricted` but there is also a label `pod-security.kubernetes.io/exempt: "true"` — this is not a valid label and does nothing. The real issue is that the pod was created BEFORE the label was applied (existing pods are not retroactively enforced).
3. Delete the pod `prometheus-agent-0` so the StatefulSet recreates it. The new pod should fail if it violates the policy.
4. Fix the StatefulSet `prometheus-agent` to comply with the `restricted` policy:
   - Set `runAsNonRoot: true`, `runAsUser: 65534`, `runAsGroup: 65534` in the pod securityContext
   - Set `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]`, `readOnlyRootFilesystem: true`, `seccompProfile.type: RuntimeDefault` on each container
   - Add an `emptyDir` volume at `/prometheus` for data storage and at `/tmp` for temporary files
5. Verify the pod starts successfully and is NOT running as root.

---

### Task 17 (6 points) — Medium
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context secure-cluster`
**Cluster:** Properly configured reference cluster.

**Task:**
Configure an ImagePolicyWebhook admission controller to enforce that only images from trusted registries are allowed.

1. SSH to `secure-cp` using `ssh secure-cp`.
2. The ImagePolicyWebhook backend is already running at `https://image-bouncer.kube-system.svc:8080/image_policy`. Create the admission configuration file at `/etc/kubernetes/admission/image-policy-config.yaml`:
   ```
   apiVersion: apiserver.config.k8s.io/v1
   kind: AdmissionConfiguration
   plugins:
   - name: ImagePolicyWebhook
     configuration:
       imagePolicy:
         kubeConfigFile: /etc/kubernetes/admission/image-policy-kubeconfig.yaml
         allowTTL: 50
         denyTTL: 50
         retryBackoff: 500
         defaultAllow: false
   ```
3. Create the kubeconfig file at `/etc/kubernetes/admission/image-policy-kubeconfig.yaml` that points the webhook to `https://image-bouncer.kube-system.svc:8080/image_policy` using the certificate at `/etc/kubernetes/pki/admission-ca.crt`.
4. Add `ImagePolicyWebhook` to the `--enable-admission-plugins` flag in the kube-apiserver manifest (preserve existing plugins).
5. Add the `--admission-control-config-file=/etc/kubernetes/admission/image-policy-config.yaml` flag to the kube-apiserver manifest.
6. Wait for the API server to restart and verify that pods with untrusted images are rejected.

---

### Task 18 (5 points) — Easy
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context prod-cluster`
**Cluster:** Production workloads needing security hardening.
**Namespace:** `web-tier`

**Task:**
Create a NetworkPolicy in the `web-tier` namespace to implement network segmentation.

1. Create a NetworkPolicy named `web-tier-policy` in namespace `web-tier` that:
   - Applies to all pods in the namespace (use `podSelector: {}`)
   - Allows ingress traffic only from namespaces with label `tier: frontend` on port `8080`
   - Allows egress traffic only to:
     - Pods in namespace with label `tier: backend` on port `3306`
     - DNS resolution (port 53 UDP and TCP to any destination)
   - Denies all other ingress and egress traffic
2. Verify the NetworkPolicy is created and has the correct rules: `kubectl describe networkpolicy web-tier-policy -n web-tier`.

---
---

## Mock Exam 3 — Solutions

---

### Solution 1
**API Server Not Starting — Fix Audit Policy YAML Error**

**Commands/YAML:**

```bash
# SSH to the node
ssh troubleshoot-cp

# Check API server pod status (may need to use crictl since API is down)
crictl ps -a | grep kube-apiserver
crictl logs <container-id>

# Inspect the audit policy for YAML errors
cat /etc/kubernetes/audit/policy.yaml

# Common YAML errors: wrong indentation, tabs instead of spaces, missing colons
# Use a YAML linter or check manually
python3 -c "import yaml; yaml.safe_load(open('/etc/kubernetes/audit/policy.yaml'))"
```

Fix the audit policy:

```yaml
# /etc/kubernetes/audit/policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: Metadata
    resources:
    - group: ""
      resources: ["secrets"]
  - level: RequestResponse
    resources:
    - group: ""
      resources: ["*"]
    - group: "apps"
      resources: ["*"]
    - group: "batch"
      resources: ["*"]
    - group: "networking.k8s.io"
      resources: ["*"]
```

```bash
# Validate the YAML
python3 -c "import yaml; yaml.safe_load(open('/etc/kubernetes/audit/policy.yaml')); print('Valid')"

# Wait for the API server to come back (static pod auto-restarts)
# If it doesn't restart, move the manifest out and back:
mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/
sleep 5
mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/

# Verify
crictl ps | grep kube-apiserver
```

**Fast approach:** `python3 -c "import yaml; ..."` to find the exact line with the syntax error, fix it, then wait for auto-restart.

**Verification:**
```bash
kubectl get pods -n kube-system | grep apiserver
# Should show 1/1 Running
kubectl get events -n kube-system --sort-by='.lastTimestamp' | head
```

**Points breakdown:**
- Identifying the YAML error: 1 point
- Fixing the audit policy with correct YAML syntax: 2 points
- Correct audit levels (Secrets at Metadata, rest at RequestResponse): 1 point
- API server running successfully: 1 point

---

### Solution 2
**RBAC — Remove cluster-admin and Create Scoped Role**

**Commands/YAML:**

```bash
# Find the ClusterRoleBinding
kubectl get clusterrolebindings -o wide | grep dev-deployer
# or
kubectl get clusterrolebindings -o json | jq '.items[] | select(.subjects[]?.name=="dev-deployer")'

# Delete the ClusterRoleBinding (example name: dev-deployer-admin)
kubectl delete clusterrolebinding dev-deployer-admin
```

Create the Role:

```yaml
# deployer-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployer-role
  namespace: staging
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "create", "update", "delete"]
- apiGroups: [""]
  resources: ["services"]
  verbs: ["get", "list", "create", "update", "delete"]
```

```bash
kubectl apply -f deployer-role.yaml
```

Create the RoleBinding:

```yaml
# deployer-binding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: deployer-binding
  namespace: staging
subjects:
- kind: ServiceAccount
  name: dev-deployer
  namespace: staging
roleRef:
  kind: Role
  name: deployer-role
  apiGroup: rbac.authorization.k8s.io
```

```bash
kubectl apply -f deployer-binding.yaml
```

**Fast approach:**
```bash
kubectl delete clusterrolebinding $(kubectl get clusterrolebindings -o json | jq -r '.items[] | select(.subjects[]?.name=="dev-deployer") | .metadata.name')
kubectl create role deployer-role -n staging --verb=get,list,create,update,delete --resource=deployments.apps,services
kubectl create rolebinding deployer-binding -n staging --role=deployer-role --serviceaccount=staging:dev-deployer
```

**Verification:**
```bash
kubectl auth can-i create deployments -n staging --as=system:serviceaccount:staging:dev-deployer
# yes
kubectl auth can-i create pods -n staging --as=system:serviceaccount:staging:dev-deployer
# no
kubectl auth can-i list secrets -n kube-system --as=system:serviceaccount:staging:dev-deployer
# no
```

**Points breakdown:**
- Identifying and deleting the ClusterRoleBinding: 1 point
- Correct Role with proper API groups and verbs: 2 points
- Correct RoleBinding with proper ServiceAccount reference: 1 point

---

### Solution 3
**Fix Pod SecurityContext — runAsNonRoot Failure**

**Commands/YAML:**

```bash
# Check the current state
kubectl get deployment payment-processor -n payments -o yaml
kubectl describe pod -l app=payment-processor -n payments
kubectl logs -l app=payment-processor -n payments
```

Edit the Deployment:

```bash
kubectl edit deployment payment-processor -n payments
```

Or apply this patch:

```yaml
# payment-processor-fix.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-processor
  namespace: payments
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - name: payment-processor
        image: internal-registry.example.com/payments:v2.4
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          runAsGroup: 1000
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp-volume
          mountPath: /tmp
      volumes:
      - name: tmp-volume
        emptyDir: {}
```

```bash
kubectl apply -f payment-processor-fix.yaml
```

**Fast approach:** Use `kubectl patch`:
```bash
kubectl patch deployment payment-processor -n payments --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/securityContext","value":{"runAsNonRoot":true,"runAsUser":1000,"runAsGroup":1000,"fsGroup":1000}},
  {"op":"add","path":"/spec/template/spec/containers/0/securityContext","value":{"runAsNonRoot":true,"runAsUser":1000,"runAsGroup":1000,"readOnlyRootFilesystem":true,"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]}}},
  {"op":"add","path":"/spec/template/spec/volumes","value":[{"name":"tmp-volume","emptyDir":{}}]},
  {"op":"add","path":"/spec/template/spec/containers/0/volumeMounts","value":[{"name":"tmp-volume","mountPath":"/tmp"}]}
]'
```

**Verification:**
```bash
kubectl get pods -n payments -l app=payment-processor
# Should show Running
kubectl exec -n payments deployment/payment-processor -- id
# uid=1000 gid=1000
kubectl exec -n payments deployment/payment-processor -- touch /test-file
# Should fail (read-only filesystem)
kubectl exec -n payments deployment/payment-processor -- touch /tmp/test-file
# Should succeed
```

**Points breakdown:**
- Identifying the root cause (image runs as root, need runAsUser): 1 point
- Setting correct container-level securityContext: 2 points
- Adding emptyDir for /tmp: 1 point
- readOnlyRootFilesystem + capabilities.drop ALL: 1 point
- Pod successfully running: 1 point

---

### Solution 4
**Falco Not Capturing Alerts — Kernel Module and Custom Rule**

**Commands/YAML:**

```bash
# SSH to node
ssh prod-node01

# Check Falco pod logs
kubectl logs -n falco-system -l app=falco --tail=50

# On the node, check kernel module
lsmod | grep falco
# If empty, module is not loaded

# Load the Falco kernel module
falco-driver-loader
# This compiles and inserts the kernel module

# Verify module is loaded
lsmod | grep falco
# Should show falco module
```

Create the custom rule:

```bash
# Edit /etc/falco/falco_rules.local.yaml
cat >> /etc/falco/falco_rules.local.yaml << 'EOF'

- rule: Process Execution in Payments Namespace
  desc: Detects any process execution in containers within the payments namespace
  condition: >
    spawned_process and
    container and
    k8s.ns.name = "payments"
  output: >
    Unexpected process in payments namespace
    (user=%user.name command=%proc.cmdline container=%container.name namespace=%k8s.ns.name)
  priority: WARNING
  tags: [custom, payments]
EOF
```

```bash
# Restart Falco
systemctl restart falco
# or if running as DaemonSet, delete the pod to force restart:
# kubectl delete pod -n falco-system -l app=falco --field-selector spec.nodeName=prod-node01

# Verify Falco is running
systemctl status falco
```

**Fast approach:** Load module with `falco-driver-loader`, append the custom rule in one `cat >>` command, restart Falco.

**Verification:**
```bash
# Test by running a command in a pod in payments namespace
kubectl run test-exec --image=busybox -n payments -- sleep 3600
kubectl exec -n payments test-exec -- ls
# Check Falco logs
journalctl -u falco | tail -20
# Should see "Unexpected process in payments namespace" alert
# Clean up
kubectl delete pod test-exec -n payments
```

**Points breakdown:**
- Diagnosing the kernel module issue: 1 point
- Loading the Falco kernel module: 1 point
- Creating the custom Falco rule with correct syntax: 2 points
- Correct condition, output, and priority: 1 point
- Restarting Falco and verifying alerts: 1 point

---

### Solution 5
**Trivy Image Scanning**

**Commands/YAML:**

```bash
# SSH to prod-cp
ssh prod-cp

# Scan nginx:1.23 for HIGH and CRITICAL vulnerabilities
trivy image --severity HIGH,CRITICAL nginx:1.23 > /root/trivy-nginx-report.txt

# Scan node:18-alpine for CRITICAL only
trivy image --severity CRITICAL node:18-alpine > /root/trivy-node-report.txt

# Find pods using vulnerable images in frontend namespace
# First list all pods and their images
kubectl get pods -n frontend -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.image}{"\n"}{end}{end}'
```

```bash
# For each image used in the namespace, scan it and check for CRITICAL
# Then write the pod names to the file
# Example approach:
for pod in $(kubectl get pods -n frontend -o jsonpath='{.items[*].metadata.name}'); do
  image=$(kubectl get pod $pod -n frontend -o jsonpath='{.spec.containers[0].image}')
  count=$(trivy image --severity CRITICAL --quiet "$image" 2>/dev/null | grep -c "CRITICAL")
  if [ "$count" -gt "0" ]; then
    echo "$pod" >> /root/vulnerable-pods.txt
  fi
done
```

**Fast approach:**
```bash
ssh prod-cp
trivy image --severity HIGH,CRITICAL nginx:1.23 > /root/trivy-nginx-report.txt
trivy image --severity CRITICAL node:18-alpine > /root/trivy-node-report.txt
# Manually check which pods use these images and write names
kubectl get pods -n frontend -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image --no-headers | while read name image; do
  if trivy image --severity CRITICAL -q "$image" 2>/dev/null | grep -q CRITICAL; then echo "$name"; fi
done > /root/vulnerable-pods.txt
```

**Verification:**
```bash
cat /root/trivy-nginx-report.txt | head -20
cat /root/trivy-node-report.txt | head -20
cat /root/vulnerable-pods.txt
```

**Points breakdown:**
- Correct trivy scan for nginx with HIGH,CRITICAL: 1.5 points
- Correct trivy scan for node with CRITICAL only: 1.5 points
- Correctly identified vulnerable pods in /root/vulnerable-pods.txt: 2 points

---

### Solution 6
**Fix Ingress Exposure — NetworkPolicy, TLS, and Service Type**

**Commands/YAML:**

```bash
# Delete the existing insecure Ingress
kubectl delete ingress dashboard-ingress -n internal
```

Create the NetworkPolicy:

```yaml
# dashboard-restrict.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: dashboard-restrict
  namespace: internal
spec:
  podSelector:
    matchLabels:
      app: dashboard
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: admin
    ports:
    - protocol: TCP
      port: 8443
```

```bash
kubectl apply -f dashboard-restrict.yaml
```

Change Service type:

```bash
kubectl patch svc dashboard-svc -n internal -p '{"spec":{"type":"ClusterIP"}}'
# Note: this also removes any external LoadBalancer IP
```

Create the new Ingress with TLS and basic auth:

```yaml
# dashboard-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dashboard-ingress
  namespace: internal
  annotations:
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: dashboard-auth
spec:
  tls:
  - hosts:
    - dashboard.internal.local
    secretName: dashboard-tls
  rules:
  - host: dashboard.internal.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dashboard-svc
            port:
              number: 8443
```

```bash
kubectl apply -f dashboard-ingress.yaml
```

**Fast approach:** Delete old ingress, apply NetworkPolicy YAML, patch the service, apply new Ingress YAML — four commands.

**Verification:**
```bash
kubectl get ingress -n internal
kubectl describe ingress dashboard-ingress -n internal
kubectl get svc dashboard-svc -n internal
# Type should be ClusterIP
kubectl get networkpolicy dashboard-restrict -n internal
kubectl describe networkpolicy dashboard-restrict -n internal
```

**Points breakdown:**
- Deleting old Ingress: 1 point
- Correct NetworkPolicy with podSelector and port: 2 points
- Changing Service to ClusterIP: 1 point
- New Ingress with TLS and auth annotations: 2 points
- Valid host, backend, TLS secret reference: 1 point

---

### Solution 7
**Fix Admission Controller Webhook — Incorrect Service targetPort**

**Commands/YAML:**

```bash
# Investigate the webhook
kubectl get validatingwebhookconfiguration image-policy-webhook -o yaml

# Check the webhook service
kubectl get svc image-policy-svc -n kube-system -o yaml
# Note: targetPort is 443, but the pod listens on 8443

# Check the webhook pod
kubectl get pods -n kube-system | grep image-policy
kubectl describe pod image-policy-server-0 -n kube-system
# Verify the container port is 8443

# Fix the service targetPort
kubectl patch svc image-policy-svc -n kube-system --type='json' -p='[{"op":"replace","path":"/spec/ports/0/targetPort","value":8443}]'
```

**Fast approach:**
```bash
kubectl patch svc image-policy-svc -n kube-system --type='json' -p='[{"op":"replace","path":"/spec/ports/0/targetPort","value":8443}]'
```

**Verification:**
```bash
# Verify service
kubectl get svc image-policy-svc -n kube-system -o yaml | grep targetPort
# Should show 8443

# Verify webhook pod is ready
kubectl get pod image-policy-server-0 -n kube-system
# Should show 1/1 Running

# Test pod creation
kubectl run test-webhook --image=nginx -n default
# Should succeed
kubectl delete pod test-webhook -n default
```

**Points breakdown:**
- Identifying the Service targetPort mismatch: 2 points
- Fixing the targetPort to 8443: 2 points
- Verifying pod creation works: 1 point

---

### Solution 8
**AppArmor Profile — Load and Apply**

**Commands/YAML:**

```bash
# SSH to the node
ssh secure-node01

# Inspect the AppArmor profile
cat /etc/apparmor.d/k8s-nginx-deny-write

# Check if it's loaded
aa-status | grep k8s-nginx-deny-write
# Not found — profile is not loaded

# Load the profile
apparmor_parser -r /etc/apparmor.d/k8s-nginx-deny-write

# Verify it's loaded
aa-status | grep k8s-nginx-deny-write
# Should show as enforced

# Exit back to the control plane
exit
```

Edit the Deployment to apply the profile:

```bash
kubectl edit deployment nginx-secure -n web-prod
```

Add the annotation to the pod template:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-secure
  namespace: web-prod
spec:
  template:
    metadata:
      annotations:
        container.apparmor.security.beta.kubernetes.io/nginx: localhost/k8s-nginx-deny-write
    spec:
      containers:
      - name: nginx
        # ... existing config
```

**Fast approach:**
```bash
ssh secure-node01
apparmor_parser -r /etc/apparmor.d/k8s-nginx-deny-write
aa-status | grep k8s-nginx-deny-write
exit
kubectl patch deployment nginx-secure -n web-prod --type='json' -p='[{"op":"add","path":"/spec/template/metadata/annotations","value":{"container.apparmor.security.beta.kubernetes.io/nginx":"localhost/k8s-nginx-deny-write"}}]'
```

**Verification:**
```bash
# Check pods are running
kubectl get pods -n web-prod -l app=nginx-secure
# Should show Running

# Verify AppArmor is enforced
kubectl get pod -n web-prod -l app=nginx-secure -o jsonpath='{.items[0].metadata.annotations}' | jq .
# Should include the AppArmor annotation

# Test the profile
kubectl exec -n web-prod deployment/nginx-secure -- touch /usr/share/nginx/html/test
# Should be denied: "Permission denied"
```

**Points breakdown:**
- Loading the AppArmor profile on the node: 2 points
- Verifying profile is loaded with aa-status: 1 point
- Correctly annotating the Deployment pod template: 2 points
- Pods running with profile enforced: 1 point

---

### Solution 9
**Kubelet Hardening — Fix Insecure Settings**

**Commands/YAML:**

```bash
# SSH to the node
ssh attack-worker01

# Inspect current kubelet config
cat /var/lib/kubelet/config.yaml

# Edit the config
vi /var/lib/kubelet/config.yaml
```

Fix these settings in `/var/lib/kubelet/config.yaml`:

```yaml
# Change these values:
authentication:
  anonymous:
    enabled: false    # was: true
  webhook:
    enabled: true
authorization:
  mode: Webhook       # was: AlwaysAllow
readOnlyPort: 0        # was: 10255
protectKernelDefaults: true  # was: false
```

```bash
# Restart kubelet
systemctl restart kubelet

# Verify kubelet is running
systemctl status kubelet
```

**Fast approach:**
```bash
ssh attack-worker01
sed -i 's/enabled: true/enabled: false/' /var/lib/kubelet/config.yaml
# Be careful with sed — better to use a targeted approach:
python3 -c "
import yaml
with open('/var/lib/kubelet/config.yaml') as f:
    config = yaml.safe_load(f)
config['authentication']['anonymous']['enabled'] = False
config['authorization']['mode'] = 'Webhook'
config['readOnlyPort'] = 0
config['protectKernelDefaults'] = True
with open('/var/lib/kubelet/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
"
systemctl restart kubelet
```

**Verification:**
```bash
# On the node
systemctl status kubelet
# Active: active (running)

# From the control plane (exit the SSH session first)
exit
curl -sk https://attack-worker01:10250/pods
# Should return 401 Unauthorized

# Verify read-only port is closed
curl -s http://attack-worker01:10255/pods
# Should fail: connection refused
```

**Points breakdown:**
- Setting anonymous.enabled to false: 1 point
- Setting authorization.mode to Webhook: 1 point
- Setting readOnlyPort to 0: 1 point
- Setting protectKernelDefaults to true: 1 point
- Kubelet running and anonymous access denied: 1 point

---

### Solution 10
**Identify Mutable Image Tags and Fix to Digest**

**Commands/YAML:**

```bash
# Find pods using :latest or no tag
kubectl get pods -n backend -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.image}{"\n"}{end}{end}' | grep -E ':latest|[^:]+$' | awk '{print $1}'
# Alternative:
kubectl get pods -n backend -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image --no-headers | grep -E ':latest$|^[^:]*$' | awk '{print $1}'

# Write to file
kubectl get pods -n backend -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.image}{"\n"}{end}{end}' | grep -E ':latest|[^:]*$' | awk '{print $1}' > /root/mutable-tag-pods.txt
```

```bash
# Update the api-server deployment to use the digest
kubectl set image deployment/api-server api-server='registry.example.com/api@sha256:ab3c4d5e6f7890123456789abcdef0123456789abcdef0123456789abcdef01' -n backend

# Verify rollout
kubectl rollout status deployment/api-server -n backend
```

**Fast approach:**
```bash
kubectl get pods -n backend -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.containers[0].image}{"\n"}{end}' | awk '/:latest$/ || !/:/{print $1}' > /root/mutable-tag-pods.txt
kubectl set image deployment/api-server api-server='registry.example.com/api@sha256:ab3c4d5e6f7890123456789abcdef0123456789abcdef0123456789abcdef01' -n backend
```

**Verification:**
```bash
cat /root/mutable-tag-pods.txt
kubectl get deployment api-server -n backend -o jsonpath='{.spec.template.spec.containers[0].image}'
# Should show the sha256 digest
kubectl rollout status deployment/api-server -n backend
# Should show successfully rolled out
```

**Points breakdown:**
- Correctly identifying pods with mutable tags: 2 points
- Writing correct pod names to file: 1 point
- Updating deployment to use image digest: 1 point

---

### Solution 11
**Remove hostPath Mount and Secure Redis**

**Commands/YAML:**

```bash
# Confirm the hostPath mount
kubectl get deployment redis-cache -n data-store -o yaml | grep -A5 hostPath
kubectl get deployment redis-cache -n data-store -o yaml | grep -A3 volumeMount
```

Edit the Deployment to remove the hostPath:

```bash
kubectl edit deployment redis-cache -n data-store
```

Remove the volume and volumeMount sections related to hostPath:

```yaml
# Remove this from volumes:
# - name: host-root
#   hostPath:
#     path: /
# Remove this from volumeMounts:
# - name: host-root
#   mountPath: /host
```

Label the namespace for Pod Security Admission:

```bash
kubectl label namespace data-store pod-security.kubernetes.io/enforce=restricted --overwrite
kubectl label namespace data-store pod-security.kubernetes.io/warn=restricted --overwrite
kubectl label namespace data-store pod-security.kubernetes.io/audit=restricted --overwrite
```

Create the NetworkPolicy:

```yaml
# redis-restrict.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: redis-restrict
  namespace: data-store
spec:
  podSelector:
    matchLabels:
      app: redis
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api
    ports:
    - protocol: TCP
      port: 6379
  egress:
  - ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

```bash
kubectl apply -f redis-restrict.yaml
```

Note: After labeling the namespace with `restricted`, the redis-cache Deployment will also need securityContext adjustments to comply. You may need to add:

```bash
kubectl patch deployment redis-cache -n data-store --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/securityContext","value":{"runAsNonRoot":true,"runAsUser":999,"runAsGroup":999,"fsGroup":999,"seccompProfile":{"type":"RuntimeDefault"}}},
  {"op":"add","path":"/spec/template/spec/containers/0/securityContext","value":{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]},"readOnlyRootFilesystem":true}},
  {"op":"add","path":"/spec/template/spec/volumes","value":[{"name":"redis-data","emptyDir":{}}]},
  {"op":"add","path":"/spec/template/spec/containers/0/volumeMounts","value":[{"name":"redis-data","mountPath":"/data"}]}
]'
```

**Fast approach:** `kubectl edit` the deployment to remove hostPath, apply label and NetworkPolicy YAML in parallel.

**Verification:**
```bash
kubectl get deployment redis-cache -n data-store -o yaml | grep hostPath
# Should return nothing

kubectl get ns data-store --show-labels | grep pod-security
# Should show enforce=restricted

kubectl describe networkpolicy redis-restrict -n data-store

kubectl get pods -n data-store -l app=redis
# Should be Running
```

**Points breakdown:**
- Removing hostPath volume and mount: 2 points
- Labeling namespace with pod-security restricted: 1 point
- NetworkPolicy with correct ingress (app: api, port 6379): 2 points
- NetworkPolicy with correct egress (DNS only): 1 point
- Pods running without hostPath: 1 point

---

### Solution 12
**Fix Audit Policy — Missing Events**

**Commands/YAML:**

```bash
# SSH to control plane
ssh prod-cp

# Backup existing audit policy
cp /etc/kubernetes/audit/policy.yaml /etc/kubernetes/audit/policy.yaml.bak
```

Write the corrected audit policy:

```yaml
# /etc/kubernetes/audit/policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  # Don't log health check endpoints
  - level: None
    nonResourceURLs:
    - "/healthz*"
    - "/readyz*"
    - "/livez*"

  # Log Secret access at Metadata level
  - level: Metadata
    resources:
    - group: ""
      resources: ["secrets"]

  # Log ConfigMap access at Request level
  - level: Request
    resources:
    - group: ""
      resources: ["configmaps"]

  # Log all resources in kube-system at Metadata level
  - level: Metadata
    namespaces: ["kube-system"]

  # Log exec, portforward, attach at RequestResponse level
  - level: RequestResponse
    resources:
    - group: ""
      resources: ["pods/exec", "pods/portforward", "pods/attach"]

  # Catch-all: log everything else at Request level
  - level: Request
    resources:
    - group: ""
      resources: ["*"]
    - group: "apps"
      resources: ["*"]
    - group: "batch"
      resources: ["*"]
    - group: "networking.k8s.io"
      resources: ["*"]
    - group: "rbac.authorization.k8s.io"
      resources: ["*"]
```

Ensure the kube-apiserver has the correct flags:

```bash
# Check current flags
cat /etc/kubernetes/manifests/kube-apiserver.yaml | grep audit

# Add or verify these flags in the kube-apiserver manifest:
# --audit-policy-file=/etc/kubernetes/audit/policy.yaml
# --audit-log-path=/var/log/kubernetes/audit/audit.log
# --audit-log-maxage=30
# --audit-log-maxbackup=10
# --audit-log-maxsize=100

# Make sure the audit log directory exists
mkdir -p /var/log/kubernetes/audit

# Edit the manifest if flags are missing
vi /etc/kubernetes/manifests/kube-apiserver.yaml

# Restart API server by moving manifest
mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/kube-apiserver.yaml
sleep 10
mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/

# Wait for it to come back
watch crictl ps | grep kube-apiserver
```

**Fast approach:** Write the policy file directly with `cat > /etc/kubernetes/audit/policy.yaml << 'EOF' ...`, check/fix manifest flags, cycle the static pod.

**Verification:**
```bash
# Check API server is running
crictl ps | grep kube-apiserver

# Check audit logs are being written
ls -la /var/log/kubernetes/audit/audit.log
tail -5 /var/log/kubernetes/audit/audit.log

# Trigger an auditable event
kubectl get secrets -n default
# Then check the log
grep '"resource":"secrets"' /var/log/kubernetes/audit/audit.log | tail -3
```

**Points breakdown:**
- Health check endpoints at None: 1 point
- Secrets at Metadata level: 1 point
- ConfigMaps at Request level: 0.5 points
- kube-system namespace at Metadata: 0.5 points
- pods/exec, portforward, attach at RequestResponse: 1 point
- Catch-all at Request level: 0.5 points
- Correct API server flags and log verification: 1.5 points

---

### Solution 13
**Secrets as Volumes Instead of Environment Variables**

**Commands/YAML:**

```bash
# Inspect current deployment
kubectl get deployment config-reader -n secrets-app -o yaml
```

Edit the Deployment:

```bash
kubectl edit deployment config-reader -n secrets-app
```

Modified Deployment spec:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: config-reader
  namespace: secrets-app
spec:
  template:
    spec:
      containers:
      - name: app
        # Remove all envFrom and env entries that reference secrets:
        # DELETE: envFrom:
        # DELETE: - secretRef:
        # DELETE:     name: db-credentials
        # DELETE: env:
        # DELETE: - name: API_KEY
        # DELETE:   valueFrom:
        # DELETE:     secretKeyRef:
        # DELETE:       name: api-keys
        # DELETE:       key: api-key
        env:
        - name: DB_CREDENTIALS_PATH
          value: /etc/secrets/db
        - name: API_KEYS_PATH
          value: /etc/secrets/api
        volumeMounts:
        - name: db-credentials
          mountPath: /etc/secrets/db
          readOnly: true
        - name: api-keys
          mountPath: /etc/secrets/api
          readOnly: true
      volumes:
      - name: db-credentials
        secret:
          secretName: db-credentials
          defaultMode: 0400
      - name: api-keys
        secret:
          secretName: api-keys
          defaultMode: 0400
```

**Fast approach:**
```bash
kubectl get deployment config-reader -n secrets-app -o yaml > /tmp/config-reader.yaml
# Edit the file to make the changes
vi /tmp/config-reader.yaml
kubectl apply -f /tmp/config-reader.yaml
```

**Verification:**
```bash
# Check pod is running
kubectl get pods -n secrets-app -l app=config-reader

# Verify secrets are mounted as files
kubectl exec -n secrets-app deployment/config-reader -- ls -la /etc/secrets/db/
kubectl exec -n secrets-app deployment/config-reader -- ls -la /etc/secrets/api/

# Verify file permissions
kubectl exec -n secrets-app deployment/config-reader -- stat /etc/secrets/db/password
# Should show 0400 permissions

# Verify environment variables no longer contain secret values
kubectl exec -n secrets-app deployment/config-reader -- env | grep -i password
# Should return nothing (no secret values in env)
kubectl exec -n secrets-app deployment/config-reader -- env | grep PATH
# Should show DB_CREDENTIALS_PATH=/etc/secrets/db and API_KEYS_PATH=/etc/secrets/api
```

**Points breakdown:**
- Removing envFrom and secretKeyRef env entries: 2 points
- Mounting db-credentials secret as volume at /etc/secrets/db: 1 point
- Mounting api-keys secret as volume at /etc/secrets/api: 1 point
- defaultMode: 0400 on both volumes: 1 point
- Adding path environment variables: 1 point

---

### Solution 14
**Fix Broken EncryptionConfiguration — Restore Old Key**

**Commands/YAML:**

```bash
# SSH to node
ssh troubleshoot-cp

# Check API server logs
crictl logs $(crictl ps -a --name kube-apiserver -q | head -1) 2>&1 | tail -20
# Should show "error decrypting value" errors

# Read the original key
cat /root/original-encryption-key.txt
# Example output: c2VjcmV0LWtleS0xMjM0NTY3ODkwYWJjZGVm

# Inspect current encryption config
cat /etc/kubernetes/enc/encryption-config.yaml
```

Fix the EncryptionConfiguration to include both keys:

```yaml
# /etc/kubernetes/enc/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - aescbc:
        keys:
        - name: new-key
          secret: <current-new-key-value>    # new key stays first for encrypting new Secrets
        - name: original-key
          secret: <value-from-/root/original-encryption-key.txt>  # old key added for decrypting existing Secrets
    - identity: {}
```

```bash
# Replace <value-from-...> with actual key from the backup
ORIGINAL_KEY=$(cat /root/original-encryption-key.txt)

# Edit the file to add the old key as second key
vi /etc/kubernetes/enc/encryption-config.yaml
# Add the original key as the second entry under keys:

# Restart the API server
mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/
sleep 10
mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/

# Wait for API server to start
sleep 30
crictl ps | grep kube-apiserver
```

```bash
# Verify Secrets can be read
exit  # back to control plane context
kubectl get secret -n default test-secret -o jsonpath='{.data.password}' | base64 -d

# Re-encrypt all secrets with the new key
kubectl get secrets --all-namespaces -o json | kubectl replace -f -
```

**Fast approach:** Read the original key, add it to the config file, cycle the API server, verify read, then re-encrypt all.

**Verification:**
```bash
# Verify API server is running
kubectl get nodes
# Should succeed without errors

# Verify secrets are readable
kubectl get secret test-secret -n default -o yaml
# Should show data without errors

# Verify re-encryption ran
# Optionally read directly from etcd to confirm encryption with new key:
ssh troubleshoot-cp
ETCDCTL_API=3 etcdctl --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/secrets/default/test-secret | hexdump -C | head -5
# Should show encrypted data (not plaintext)
```

**Points breakdown:**
- Identifying the issue (key mismatch): 1 point
- Adding original key as second key (not replacing new key): 2 points
- Maintaining correct key order (new first, old second): 1 point
- API server restart and Secrets readable: 1 point
- Re-encrypting all existing Secrets: 1 point

---

### Solution 15
**CIS Benchmark Remediation**

**Commands/YAML:**

```bash
# SSH to the node
ssh attack-cp

# Fix 1.1.12: etcd data directory permissions
chmod 700 /var/lib/etcd
chown etcd:etcd /var/lib/etcd
ls -la /var/lib/ | grep etcd
# Should show drwx------ etcd etcd

# Fix 1.2.6: Add kubelet-certificate-authority flag
vi /etc/kubernetes/manifests/kube-apiserver.yaml
```

Add the flag to the kube-apiserver command:

```yaml
spec:
  containers:
  - command:
    - kube-apiserver
    # ... existing flags ...
    - --kubelet-certificate-authority=/etc/kubernetes/pki/ca.crt
```

```bash
# Fix 1.2.16: Add PodSecurity admission plugin
# Find the current enable-admission-plugins line
grep "enable-admission-plugins" /etc/kubernetes/manifests/kube-apiserver.yaml
# Example: --enable-admission-plugins=NodeRestriction
# Add PodSecurity to the list:
# --enable-admission-plugins=NodeRestriction,PodSecurity

vi /etc/kubernetes/manifests/kube-apiserver.yaml
# Edit the line to add PodSecurity
```

```bash
# Wait for API server to restart automatically (static pod watcher detects changes)
sleep 30
crictl ps | grep kube-apiserver

# If it doesn't restart, cycle manually:
# mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/
# sleep 5
# mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
```

**Fast approach:**
```bash
ssh attack-cp
chmod 700 /var/lib/etcd && chown etcd:etcd /var/lib/etcd
# Use sed to add flags:
sed -i '/--kubelet-client-key/a\    - --kubelet-certificate-authority=/etc/kubernetes/pki/ca.crt' /etc/kubernetes/manifests/kube-apiserver.yaml
sed -i 's/--enable-admission-plugins=\(.*\)/--enable-admission-plugins=\1,PodSecurity/' /etc/kubernetes/manifests/kube-apiserver.yaml
```

**Verification:**
```bash
# Verify etcd permissions
stat /var/lib/etcd
# Permissions: 0700, Owner: etcd

# Verify API server flags
kubectl -n kube-system get pod kube-apiserver-attack-cp -o yaml | grep -E "kubelet-certificate-authority|enable-admission-plugins"
# Should show both flags

# Or check the process
ps aux | grep kube-apiserver | grep kubelet-certificate-authority
ps aux | grep kube-apiserver | grep PodSecurity
```

**Points breakdown:**
- etcd directory permissions set to 700 with etcd:etcd ownership: 1.5 points
- kubelet-certificate-authority flag added: 1.5 points
- PodSecurity admission plugin added (without removing existing plugins): 1.5 points
- API server successfully running after changes: 0.5 points

---

### Solution 16
**Container Running as Root Despite Pod Security Admission**

**Commands/YAML:**

```bash
# Check the namespace labels
kubectl get ns monitoring --show-labels
# Should show pod-security.kubernetes.io/enforce: restricted

# Check the pod
kubectl get pod prometheus-agent-0 -n monitoring -o yaml | grep -A5 securityContext
# May show no securityContext or runAsUser: 0

# The pod was created before the label was applied — PSA doesn't retroactively enforce
# Delete the pod so the StatefulSet recreates it
kubectl delete pod prometheus-agent-0 -n monitoring
# The new pod will fail because it violates restricted policy
```

Fix the StatefulSet:

```bash
kubectl edit statefulset prometheus-agent -n monitoring
```

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: prometheus-agent
  namespace: monitoring
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 65534
        runAsGroup: 65534
        fsGroup: 65534
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: prometheus
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
          readOnlyRootFilesystem: true
          seccompProfile:
            type: RuntimeDefault
        volumeMounts:
        - name: prometheus-data
          mountPath: /prometheus
        - name: tmp
          mountPath: /tmp
      volumes:
      - name: prometheus-data
        emptyDir: {}
      - name: tmp
        emptyDir: {}
```

**Fast approach:**
```bash
kubectl delete pod prometheus-agent-0 -n monitoring
# Wait for it to fail, then patch the StatefulSet:
kubectl patch statefulset prometheus-agent -n monitoring --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/securityContext","value":{"runAsNonRoot":true,"runAsUser":65534,"runAsGroup":65534,"fsGroup":65534,"seccompProfile":{"type":"RuntimeDefault"}}},
  {"op":"add","path":"/spec/template/spec/containers/0/securityContext","value":{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]},"readOnlyRootFilesystem":true,"seccompProfile":{"type":"RuntimeDefault"}}},
  {"op":"add","path":"/spec/template/spec/volumes/-","value":{"name":"prometheus-data","emptyDir":{}}},
  {"op":"add","path":"/spec/template/spec/volumes/-","value":{"name":"tmp","emptyDir":{}}},
  {"op":"add","path":"/spec/template/spec/containers/0/volumeMounts/-","value":{"name":"prometheus-data","mountPath":"/prometheus"}},
  {"op":"add","path":"/spec/template/spec/containers/0/volumeMounts/-","value":{"name":"tmp","mountPath":"/tmp"}}
]'
# Delete the pod again to pick up changes
kubectl delete pod prometheus-agent-0 -n monitoring
```

**Verification:**
```bash
kubectl get pod prometheus-agent-0 -n monitoring
# Should be Running

kubectl exec -n monitoring prometheus-agent-0 -- id
# uid=65534(nobody) gid=65534(nogroup)

kubectl exec -n monitoring prometheus-agent-0 -- cat /proc/1/status | grep -i seccomp
# Should show seccomp enabled
```

**Points breakdown:**
- Understanding PSA doesn't retroactively enforce: 1 point
- Deleting the pod to trigger re-evaluation: 1 point
- Correct pod securityContext (runAsNonRoot, runAsUser, runAsGroup): 1 point
- Correct container securityContext (allowPrivilegeEscalation, capabilities, readOnlyRootFilesystem, seccompProfile): 1.5 points
- emptyDir volumes for /prometheus and /tmp: 0.5 points
- Pod successfully running: 1 point

---

### Solution 17
**Configure ImagePolicyWebhook Admission Controller**

**Commands/YAML:**

```bash
# SSH to control plane
ssh secure-cp

# Create the admission control directory if needed
mkdir -p /etc/kubernetes/admission
```

Create the admission configuration:

```yaml
# /etc/kubernetes/admission/image-policy-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: ImagePolicyWebhook
  configuration:
    imagePolicy:
      kubeConfigFile: /etc/kubernetes/admission/image-policy-kubeconfig.yaml
      allowTTL: 50
      denyTTL: 50
      retryBackoff: 500
      defaultAllow: false
```

Create the kubeconfig file:

```yaml
# /etc/kubernetes/admission/image-policy-kubeconfig.yaml
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority: /etc/kubernetes/pki/admission-ca.crt
    server: https://image-bouncer.kube-system.svc:8080/image_policy
  name: image-bouncer
contexts:
- context:
    cluster: image-bouncer
    user: api-server
  name: image-bouncer
current-context: image-bouncer
users:
- name: api-server
  user:
    client-certificate: /etc/kubernetes/pki/apiserver.crt
    client-key: /etc/kubernetes/pki/apiserver.key
```

Update the kube-apiserver manifest:

```bash
vi /etc/kubernetes/manifests/kube-apiserver.yaml

# Add to the command arguments:
# - --enable-admission-plugins=...,ImagePolicyWebhook  (append to existing list)
# - --admission-control-config-file=/etc/kubernetes/admission/image-policy-config.yaml

# Add volume mount for the admission directory:
# volumeMounts:
# - name: admission-config
#   mountPath: /etc/kubernetes/admission
#   readOnly: true
# volumes:
# - name: admission-config
#   hostPath:
#     path: /etc/kubernetes/admission
#     type: DirectoryOrCreate
```

```bash
# Wait for API server to restart
sleep 30
crictl ps | grep kube-apiserver
```

**Fast approach:**
```bash
ssh secure-cp
mkdir -p /etc/kubernetes/admission
cat > /etc/kubernetes/admission/image-policy-config.yaml << 'EOF'
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: ImagePolicyWebhook
  configuration:
    imagePolicy:
      kubeConfigFile: /etc/kubernetes/admission/image-policy-kubeconfig.yaml
      allowTTL: 50
      denyTTL: 50
      retryBackoff: 500
      defaultAllow: false
EOF

cat > /etc/kubernetes/admission/image-policy-kubeconfig.yaml << 'EOF'
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority: /etc/kubernetes/pki/admission-ca.crt
    server: https://image-bouncer.kube-system.svc:8080/image_policy
  name: image-bouncer
contexts:
- context:
    cluster: image-bouncer
    user: api-server
  name: image-bouncer
current-context: image-bouncer
users:
- name: api-server
  user:
    client-certificate: /etc/kubernetes/pki/apiserver.crt
    client-key: /etc/kubernetes/pki/apiserver.key
EOF

# Edit the kube-apiserver manifest
sed -i 's/--enable-admission-plugins=\(.*\)/--enable-admission-plugins=\1,ImagePolicyWebhook/' /etc/kubernetes/manifests/kube-apiserver.yaml
# Add admission-control-config-file flag
sed -i '/--enable-admission-plugins/a\    - --admission-control-config-file=/etc/kubernetes/admission/image-policy-config.yaml' /etc/kubernetes/manifests/kube-apiserver.yaml
```

**Verification:**
```bash
# Check API server is running
exit
kubectl get nodes

# Test with an untrusted image
kubectl run test-untrusted --image=docker.io/malicious/backdoor:latest -n default
# Should be rejected by the webhook

# Test with a trusted image (depends on webhook configuration)
kubectl run test-trusted --image=registry.internal.com/nginx:1.25 -n default
# Should succeed (if the webhook allows this registry)
```

**Points breakdown:**
- Creating correct AdmissionConfiguration file: 1.5 points
- Creating correct kubeconfig file with proper server URL and certs: 1.5 points
- Adding ImagePolicyWebhook to admission plugins (preserving existing): 1 point
- Adding admission-control-config-file flag: 1 point
- API server running and webhook working: 1 point

---

### Solution 18
**NetworkPolicy for Web-Tier Segmentation**

**Commands/YAML:**

```yaml
# web-tier-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-tier-policy
  namespace: web-tier
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          tier: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          tier: backend
    ports:
    - protocol: TCP
      port: 3306
  - ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

```bash
kubectl apply -f web-tier-policy.yaml
```

**Fast approach:**
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-tier-policy
  namespace: web-tier
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          tier: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          tier: backend
    ports:
    - protocol: TCP
      port: 3306
  - ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
EOF
```

**Verification:**
```bash
kubectl get networkpolicy web-tier-policy -n web-tier
kubectl describe networkpolicy web-tier-policy -n web-tier
# Verify:
# - podSelector: {} (applies to all pods)
# - Ingress: from namespaces with tier=frontend on port 8080
# - Egress: to namespaces with tier=backend on port 3306, plus DNS
# - PolicyTypes: Ingress, Egress (denies all other traffic)
```

**Points breakdown:**
- podSelector: {} (all pods in namespace): 1 point
- Correct ingress rule (namespaceSelector + port 8080): 1.5 points
- Correct egress to backend (namespaceSelector + port 3306): 1.5 points
- DNS egress rule (UDP and TCP port 53): 1 point

---

## Mock Exam 3 — Scoring Guide

### Points Distribution by Task

| Task | Domain | Difficulty | Points |
|------|--------|-----------|--------|
| 1 | Cluster Setup | Hard | 5 |
| 2 | Cluster Hardening | Medium | 4 |
| 3 | Minimize Microservice Vulnerabilities | Hard | 6 |
| 4 | Monitoring, Logging and Runtime Security | Hard | 6 |
| 5 | Supply Chain Security | Medium | 5 |
| 6 | Cluster Setup | Hard | 7 |
| 7 | Supply Chain Security | Medium | 5 |
| 8 | System Hardening | Hard | 6 |
| 9 | Cluster Hardening | Hard | 6 |
| 10 | Supply Chain Security | Easy | 4 |
| 11 | Minimize Microservice Vulnerabilities | Hard | 7 |
| 12 | Monitoring, Logging and Runtime Security | Medium | 6 |
| 13 | Minimize Microservice Vulnerabilities | Medium | 6 |
| 14 | Cluster Setup | Hard | 6 |
| 15 | Cluster Hardening | Medium | 5 |
| 16 | Monitoring, Logging and Runtime Security | Medium | 5 |
| 17 | Supply Chain Security | Medium | 6 |
| 18 | Minimize Microservice Vulnerabilities | Easy | 5 |
| **Total** | | | **100** |

### Points by Domain

| Domain | Tasks | Total Points | Weight |
|--------|-------|-------------|--------|
| Cluster Setup | 1, 6, 14 | 18 | 18% |
| Cluster Hardening | 2, 9, 15 | 15 | 15% |
| System Hardening | 8 | 6 | 6% |
| Minimize Microservice Vulnerabilities | 3, 11, 13, 18 | 24 | 24% |
| Supply Chain Security | 5, 7, 10, 17 | 20 | 20% |
| Monitoring, Logging and Runtime Security | 4, 12, 16 | 17 | 17% |

### Points by Difficulty

| Difficulty | Tasks | Total Points |
|-----------|-------|-------------|
| Easy (2) | 10, 18 | 9 |
| Medium (8) | 2, 5, 7, 12, 13, 15, 16, 17 | 42 |
| Hard (8) | 1, 3, 4, 6, 8, 9, 11, 14 | 49 |

### Passing Score: 67 points (67%)

### Score Interpretation

| Score Range | Assessment |
|------------|-----------|
| 90-100 | Excellent — ready for the exam with confidence |
| 80-89 | Strong — minor areas to tighten up |
| 67-79 | Pass — but under time pressure you may struggle; focus on speed |
| 55-66 | Close — review troubleshooting methodology and practice common patterns |
| 40-54 | Needs work — revisit weaker domains systematically |
| Below 40 | Significant preparation needed — focus on fundamentals first |

### Weak Area Analysis

**If you missed Tasks 1, 6, 14:** Your Cluster Setup knowledge needs work. Focus on: audit policies, EncryptionConfiguration, Ingress security, TLS. Practice fixing broken API server configurations — this is a very common exam pattern.

**If you missed Tasks 2, 9, 15:** Cluster Hardening is weak. Review: RBAC scoping, kubelet security settings, CIS benchmark remediations. These are high-frequency exam topics.

**If you missed Task 8:** System Hardening needs attention. Practice: AppArmor profile loading and pod annotation, seccomp profiles, Linux capabilities.

**If you missed Tasks 3, 11, 13, 18:** Minimize Microservice Vulnerabilities is your weakest area. This is a 20% domain. Focus on: SecurityContext (runAsNonRoot, readOnlyRootFilesystem, capabilities), Pod Security Admission, Secrets as volumes, NetworkPolicies.

**If you missed Tasks 5, 7, 10, 17:** Supply Chain Security needs improvement. Practice: Trivy scanning, image digests vs tags, ImagePolicyWebhook configuration, admission controller debugging.

**If you missed Tasks 4, 12, 16:** Monitoring, Logging and Runtime Security is lacking. Review: Falco rules and troubleshooting, audit policy syntax (the order of rules matters!), Pod Security Admission enforcement behavior.

### Time Management Tips for This Exam

With 18 tasks and 120 minutes, **you cannot spend more than 7 minutes per task on average**.

**Recommended approach:**
1. **First pass (0-40 min):** Complete Tasks 10, 18 (Easy) and Tasks 2, 5, 7 (straightforward Medium) — bank ~23 points.
2. **Second pass (40-80 min):** Tackle Tasks 12, 13, 15, 16, 17 (remaining Medium) — target ~28 points.
3. **Final pass (80-120 min):** Attack Hard tasks 1, 3, 6, 8, 9, 11, 14, 4 in order of confidence — every point counts.

**If stuck on any single task for over 5 minutes:** Move on. Come back if time permits. Partial credit is available — write what you can and continue.

---

## Mock Exam 4: Harder Than Real Exam

**Duration:** 120 minutes | **Tasks:** 16 | **Total Points:** 100 | **Passing Score:** 67 points (67%)
**Difficulty:** Very Hard — Stretch exam for building confidence
**Kubernetes Version:** v1.35

### Exam Environment
- Cluster `enterprise-prod`: Large production cluster (1 control-plane + 5 workers), Kubernetes v1.35
- Cluster `enterprise-staging`: Staging mirror (1 control-plane + 2 workers), Kubernetes v1.35
- Cluster `dmz-cluster`: DMZ/edge cluster with external exposure (1 control-plane + 1 worker)
- Node `infra-node`: Infrastructure node with direct SSH access

**Instructions:** Complete all tasks within the allotted time. Tasks are intentionally complex and multi-step. You may use https://kubernetes.io/docs and https://github.com/kubernetes during the exam.

**Warning:** This exam is significantly harder than the actual CKS. If you can pass this with 67%+, you are well-prepared for the real exam.

---

### Task 1 (8 points) — Hard
**Domain:** Cluster Setup
**Context:** `kubectl config use-context enterprise-prod`
**Cluster:** Large production cluster (1 control-plane node `cp-prod`, 5 workers)

**Task:**
Create a comprehensive audit policy at `/etc/kubernetes/audit/policy.yaml` on the control-plane node `cp-prod` with the following rules, **in this exact order of precedence**:

1. **RequestResponse** level for all resources in the `sensitive-apps` namespace — log full request and response bodies
2. **Request** level for `secrets`, `configmaps`, and `tokenreviews` in **all namespaces** — log the request body but omit the response
3. **Metadata** level for all resources in the `apps/v1` and `batch/v1` API groups
4. **None** level for all requests to `/healthz`, `/readyz`, and `/livez` endpoints — these should not be logged at all
5. A catch-all rule: **Metadata** level for everything else

After creating the policy, configure the kube-apiserver to use this policy with the following settings:
- Audit log path: `/var/log/kubernetes/audit/audit.log`
- Maximum audit log file size: 200 MB
- Maximum number of retained audit log files: 5
- Maximum number of days to retain old audit log files: 30

Ensure the kube-apiserver restarts successfully with the new configuration. Verify that audit events are being written to the log file.

---

### Task 2 (8 points) — Hard
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context enterprise-prod`
**Cluster:** Large production cluster

**Task:**
Implement a complete **zero-trust namespace** called `payment-gateway` with all of the following security controls:

1. **Pod Security Admission**: Apply the `restricted` profile at the `enforce` level, `restricted` at `warn`, and `restricted` at `audit` — all pinned to version `v1.35`

2. **Default-deny NetworkPolicy**: Create a NetworkPolicy named `default-deny-all` that denies ALL ingress and ALL egress traffic for every pod in the namespace

3. **Selective allow NetworkPolicy**: Create a NetworkPolicy named `allow-payment-flow` that:
   - Allows pods with label `app: payment-api` to receive ingress traffic on port 8443 (TCP) ONLY from pods with label `app: api-gateway` in namespace `frontend` (namespace has label `kubernetes.io/metadata.name: frontend`)
   - Allows pods with label `app: payment-api` to send egress traffic on port 5432 (TCP) ONLY to pods with label `app: postgres` in namespace `database`
   - Allows all pods in `payment-gateway` to send egress DNS queries on port 53 (TCP and UDP) to the `kube-system` namespace

4. **ResourceQuota** named `payment-quota`: max 10 pods, 8 CPU requests, 16Gi memory requests, 16 CPU limits, 32Gi memory limits, 5 PVCs, no NodePort services allowed

5. **LimitRange** named `payment-limits`: default container request of 100m CPU and 128Mi memory, default container limit of 500m CPU and 512Mi memory, max container limit of 2 CPU and 4Gi memory

6. **RBAC**: Create a Role `payment-developer` that allows get/list/watch on pods, services, configmaps, and create/delete on pods. Create a RoleBinding `payment-dev-binding` that binds this role to the group `payment-team`.

---

### Task 3 (7 points) — Hard
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context enterprise-staging`
**Cluster:** Staging cluster (1 control-plane + 2 workers)

**Task:**
A Kyverno policy engine is already installed on the `enterprise-staging` cluster.

Create a Kyverno `ClusterPolicy` named `restrict-container-privileges` that enforces the following rules:

1. **Rule `block-privileged`**: Block any Pod that has a container or initContainer with `securityContext.privileged: true`. The violation message should read: `"Privileged containers are not allowed. Set securityContext.privileged to false."`

2. **Rule `block-host-networking`**: Block any Pod that has `hostNetwork: true`, `hostPID: true`, or `hostIPC: true`. The violation message should read: `"Host-level namespaces (hostNetwork, hostPID, hostIPC) are forbidden."`

3. **Rule `require-non-root`**: Block any Pod where any container or initContainer does NOT have `runAsNonRoot: true` set in its securityContext. The violation message should read: `"All containers must set securityContext.runAsNonRoot to true."`

4. **Rule `restrict-registries`**: Block any Pod that uses an image NOT from the following allowed registries: `registry.enterprise.internal/`, `docker.io/library/`, `gcr.io/enterprise-project/`. The violation message should read: `"Images must come from approved registries only."`

All rules must have `validationFailureAction: Enforce` and should apply to both Pods created directly and Pods created by higher-level controllers (Deployments, StatefulSets, DaemonSets, Jobs, CronJobs).

After creating the policy, verify it works by attempting to create a Pod with `image: nginx` (should be blocked — not from an approved registry) and a Pod with `image: registry.enterprise.internal/nginx:1.25` and `runAsNonRoot: true`, `privileged: false` (should succeed).

---

### Task 4 (7 points) — Hard
**Domain:** Monitoring, Logging and Runtime Security
**Context:** `kubectl config use-context enterprise-prod`
**Cluster:** Large production cluster

**Task:**
Falco is already installed on all worker nodes as a DaemonSet in namespace `falco-system`.

Create a custom Falco rules file at `/etc/falco/rules.d/custom-enterprise.yaml` on **all worker nodes** (`worker-1` through `worker-5`) containing the following rules:

1. **Rule `Unauthorized Package Manager Execution`**: Trigger a **CRITICAL** alert when any process from the list (`apt`, `apt-get`, `yum`, `dnf`, `apk`, `pip`, `pip3`, `npm`) is executed inside any container. Output should include: timestamp, container ID, container name, user, the command executed, and the parent process name. Priority: CRITICAL.

2. **Rule `Sensitive Mount Detected`**: Trigger a **WARNING** alert when any container mounts `/etc/shadow`, `/etc/passwd`, `/root/.ssh`, or `/var/run/docker.sock` from the host. Output should include container name, image, mount source and destination. Priority: WARNING.

3. **Rule `Reverse Shell Detected`**: Trigger an **EMERGENCY** alert when any process inside a container creates an outbound network connection AND the process is a shell (`bash`, `sh`, `dash`, `zsh`, `csh`) AND the file descriptor references a network socket. Output should include container name, process name, user, connection IP and port. Priority: EMERGENCY.

4. **Rule `Crypto Mining Indicator`**: Trigger a **CRITICAL** alert when any process inside a container connects to ports commonly used for crypto mining pools (3333, 4444, 5555, 8333, 9999, 14444, 14433) OR when process names match known miners (`xmrig`, `minerd`, `cpuminer`, `cgminer`). Priority: CRITICAL.

After deploying the rules, restart the Falco DaemonSet and verify that the rules are loaded by checking Falco logs.

---

### Task 5 (6 points) — Medium
**Domain:** Cluster Hardening
**Context:** `kubectl config use-context enterprise-prod`
**Cluster:** Large production cluster

**Task:**
Several ServiceAccounts in the cluster have excessive permissions. Perform the following remediations:

1. In namespace `monitoring`, a ServiceAccount `metrics-collector` is bound via a ClusterRoleBinding `metrics-full-access` to the ClusterRole `cluster-admin`. This is excessive. Create a new ClusterRole named `metrics-reader` that allows ONLY `get`, `list`, `watch` on the following resources: `pods`, `nodes`, `services`, `endpoints` and `pods/metrics`, `nodes/metrics` in the `metrics.k8s.io` API group. Update the ClusterRoleBinding `metrics-full-access` to use the new `metrics-reader` ClusterRole instead of `cluster-admin`.

2. In namespace `ci-cd`, a ServiceAccount `deploy-bot` has `automountServiceAccountToken: true` (default). The pods using this ServiceAccount only need the token during deployment. Modify the ServiceAccount to set `automountServiceAccountToken: false`. Then update the existing Deployment `deploy-runner` in the `ci-cd` namespace to explicitly set `automountServiceAccountToken: true` ONLY on the Pod spec (overriding the ServiceAccount-level setting), since this specific Deployment legitimately needs the token.

3. Find and delete ALL Secrets of type `kubernetes.io/service-account-token` in namespace `legacy-apps` that are not currently mounted by any running Pod. (There should be 3 such orphaned secrets.)

---

### Task 6 (7 points) — Hard
**Domain:** System Hardening
**Context:** SSH to `infra-node`
**Cluster/Node:** Infrastructure node with direct SSH access

**Task:**
Harden the node `infra-node` with a combined security profile applying **all three** kernel-level mechanisms to a container workload:

1. **AppArmor**: Create an AppArmor profile called `k8s-restricted-profile` at `/etc/apparmor.d/k8s-restricted-profile` that:
   - Denies all file writes except to `/tmp/**` and `/var/log/app/**`
   - Denies all network raw access
   - Denies mounting of any filesystem
   - Allows read access to `/etc/hostname`, `/etc/resolv.conf`, `/etc/hosts`
   - Allows network TCP and UDP (inet stream, inet dgram)
   Load the profile using `apparmor_parser`.

2. **Seccomp**: Create a custom Seccomp profile at `/var/lib/kubelet/seccomp/profiles/restricted-syscalls.json` that:
   - Uses `SCMP_ACT_ERRNO` as the default action (deny all by default)
   - Allows ONLY the following syscalls: `read`, `write`, `open`, `close`, `stat`, `fstat`, `lstat`, `poll`, `lseek`, `mmap`, `mprotect`, `munmap`, `brk`, `rt_sigaction`, `rt_sigprocmask`, `rt_sigreturn`, `ioctl`, `access`, `pipe`, `select`, `sched_yield`, `mremap`, `msync`, `mincore`, `madvise`, `dup`, `dup2`, `pause`, `nanosleep`, `getpid`, `socket`, `connect`, `accept`, `sendto`, `recvfrom`, `bind`, `listen`, `clone`, `execve`, `exit`, `wait4`, `kill`, `uname`, `fcntl`, `flock`, `fsync`, `ftruncate`, `getcwd`, `chdir`, `mkdir`, `rmdir`, `link`, `unlink`, `readlink`, `chmod`, `chown`, `gettimeofday`, `getuid`, `getgid`, `geteuid`, `getegid`, `getppid`, `getpgrp`, `setpgid`, `getrlimit`, `getrusage`, `sysinfo`, `times`, `futex`, `set_tid_address`, `clock_gettime`, `clock_getres`, `exit_group`, `epoll_create`, `epoll_ctl`, `epoll_wait`, `openat`, `mkdirat`, `newfstatat`, `unlinkat`, `renameat`, `readlinkat`, `fchmodat`, `faccessat`, `set_robust_list`, `arch_prctl`, `prlimit64`, `getrandom`, `close_range`, `rseq`

3. **Sysctl parameters**: After returning to the `enterprise-prod` context, create a Pod named `hardened-workload` in namespace `secure-runtime` using image `registry.enterprise.internal/app:v2.1` that:
   - Uses the AppArmor profile `k8s-restricted-profile` from the node
   - Uses the Seccomp profile `restricted-syscalls.json` from localhost
   - Sets these safe sysctl parameters: `net.ipv4.ip_unprivileged_port_start=1024`, `net.ipv4.tcp_syncookies=1`
   - Runs as user 1000, group 1000, `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, drops ALL capabilities

---

### Task 7 (5 points) — Medium
**Domain:** Cluster Setup
**Context:** `kubectl config use-context dmz-cluster`
**Cluster:** DMZ/edge cluster with external exposure

**Task:**
The `dmz-cluster` has CIS Benchmark violations that need remediation. SSH to the control-plane node `cp-dmz` and fix the following:

1. The kube-apiserver currently allows anonymous authentication. Disable anonymous authentication by setting the appropriate flag.

2. The kube-apiserver does not have the `--kubelet-certificate-authority` flag set. The kubelet CA certificate is available at `/etc/kubernetes/pki/ca.crt`. Configure the API server to use this CA for verifying kubelet serving certificates.

3. The `--authorization-mode` flag on kube-apiserver currently includes `AlwaysAllow`. Change it to use `Node,RBAC` only.

4. The etcd server is configured without peer TLS. Configure etcd peer communication to use the existing certificates:
   - Peer cert: `/etc/kubernetes/pki/etcd/peer.crt`
   - Peer key: `/etc/kubernetes/pki/etcd/peer.key`
   - Peer trusted CA: `/etc/kubernetes/pki/etcd/ca.crt`
   - Set `peer-client-cert-auth` to `true`

Ensure all components restart and the cluster is functional after changes.

---

### Task 8 (7 points) — Hard
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context enterprise-prod`
**Cluster:** Large production cluster

**Task:**
Implement a complete image supply chain security workflow:

1. Use `trivy` (available at `/usr/local/bin/trivy`) to scan the image `registry.enterprise.internal/webapp:v3.2` for vulnerabilities. Save the scan results in JSON format to `/root/trivy-reports/webapp-v3.2.json`.

2. Examine the scan results. The image contains several CRITICAL and HIGH vulnerabilities. The Dockerfile for this image is available at `/root/dockerfiles/webapp/Dockerfile`. The current Dockerfile uses `FROM ubuntu:20.04`. Update the Dockerfile to:
   - Change the base image to `ubuntu:24.04` (the patched version)
   - Add `RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*` as the second layer to ensure all packages are patched
   - Ensure the final image runs as a non-root user (add `USER 1001` before the CMD instruction if not already present)

3. A Kubernetes `ImagePolicyWebhook` admission controller configuration exists at `/etc/kubernetes/admission/image-policy-config.yaml`. The configuration currently points to a webhook at `https://image-scanner.enterprise.internal:8443/scan`. However, the API server is not configured to use it. Update the API server manifest to:
   - Enable the `ImagePolicyWebhook` admission plugin
   - Set the `--admission-control-config-file` to `/etc/kubernetes/admission/admission-config.yaml`
   - The admission configuration file `/etc/kubernetes/admission/admission-config.yaml` should reference the ImagePolicyWebhook config and set `defaultAllow: false` (deny images when webhook is unreachable)

4. Verify the API server restarts successfully.

---

### Task 9 (6 points) — Medium
**Domain:** Cluster Hardening
**Context:** `kubectl config use-context enterprise-staging`
**Cluster:** Staging cluster

**Task:**
Implement certificate-based security improvements:

1. A user named `security-auditor` needs access to the cluster. A CSR file exists at `/root/certs/security-auditor.csr`. Create a Kubernetes `CertificateSigningRequest` resource named `security-auditor-csr` with the existing CSR data, `signerName: kubernetes.io/kube-apiserver-client`, usages `digital signature` and `key encipherment` and `client auth`, and `expirationSeconds` set to 86400 (24 hours). Approve the CSR.

2. After approval, extract the signed certificate and save it to `/root/certs/security-auditor.crt`.

3. Create a ClusterRole named `security-audit-role` that allows:
   - `get`, `list`, `watch` on `pods`, `services`, `deployments`, `replicasets`, `statefulsets`, `daemonsets`, `jobs`, `cronjobs` in all API groups
   - `get`, `list`, `watch` on `networkpolicies`, `ingresses`
   - `get`, `list`, `watch` on `roles`, `rolebindings`, `clusterroles`, `clusterrolebindings`
   - `get`, `list` on `secrets` (but NOT `watch` on secrets)

4. Create a ClusterRoleBinding named `security-auditor-binding` binding `security-audit-role` to user `security-auditor`.

---

### Task 10 (7 points) — Hard
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context enterprise-prod`
**Cluster:** Large production cluster

**Task:**
Configure encryption at rest for Kubernetes Secrets and complete an etcd security workflow:

1. Create an `EncryptionConfiguration` at `/etc/kubernetes/encryption/config.yaml` on the control-plane node `cp-prod` with the following settings:
   - Resource: `secrets`
   - Provider order: `aescbc` (primary, key name `secret-key-1`, key is a 32-byte base64-encoded value — use `k8s-encryption-key-2026-prod-001` base64-encoded), then `identity` (fallback for reading unencrypted)
   - Resource: `configmaps`
   - Provider order: `aesgcm` (primary, key name `configmap-key-1`, same base64-encoded key as above), then `identity`

2. Configure the kube-apiserver to use this encryption configuration via the `--encryption-provider-config` flag. Ensure the file is properly mounted into the API server pod.

3. After the API server restarts, re-encrypt all existing secrets in the `default` namespace so they are encrypted with the new provider:
   ```
   kubectl get secrets -n default -o json | kubectl replace -f -
   ```

4. Create a snapshot (backup) of etcd and save it to `/root/etcd-backups/snapshot-$(date +%Y%m%d).db`. Use the etcd certificates located at:
   - CA: `/etc/kubernetes/pki/etcd/ca.crt`
   - Cert: `/etc/kubernetes/pki/etcd/server.crt`
   - Key: `/etc/kubernetes/pki/etcd/server.key`

5. Verify the snapshot integrity using `etcdutl snapshot status`.

---

### Task 11 (6 points) — Medium
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context enterprise-prod`
**Cluster:** Large production cluster

**Task:**
Create a `RuntimeClass` and deploy a sandboxed workload:

1. Create a `RuntimeClass` named `gvisor-sandbox` with handler `runsc`. Set scheduling node selectors to only target nodes with label `runtime: gvisor` (nodes `worker-3` and `worker-4` already have this label).

2. Create a Deployment named `sandboxed-app` in namespace `sandbox-workloads` (create the namespace if it doesn't exist):
   - Image: `registry.enterprise.internal/microservice:v1.4`
   - Replicas: 2
   - Use the `gvisor-sandbox` RuntimeClass
   - Set `securityContext` at pod level: `runAsNonRoot: true`, `runAsUser: 65534`, `runAsGroup: 65534`, `fsGroup: 65534`, `seccompProfile.type: RuntimeDefault`
   - Set `securityContext` at container level: `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, capabilities drop ALL
   - Add a writable `emptyDir` volume mounted at `/tmp`
   - Resource requests: 100m CPU, 128Mi memory; limits: 500m CPU, 512Mi memory

3. Verify the pods are running and using the gVisor runtime by checking the `runtimeClassName` in the pod spec and confirming the pods are scheduled on nodes with the `runtime: gvisor` label.

---

### Task 12 (6 points) — Medium
**Domain:** Monitoring, Logging and Runtime Security
**Context:** `kubectl config use-context enterprise-prod`
**Cluster:** Large production cluster

**Task:**
An incident has been detected in the cluster. Suspicious activity was observed in namespace `compromised-ns`. Investigate and remediate:

1. Check all running pods in `compromised-ns`. Identify any pods that:
   - Are running as root (UID 0)
   - Have `privileged: true` in their security context
   - Have unusual processes running (crypto miners, reverse shells)
   Use `kubectl exec` to inspect running processes with `ps aux` or check the container's process list.

2. A pod named `web-debug` in namespace `compromised-ns` is running a suspicious binary. Examine its network connections using `kubectl exec web-debug -n compromised-ns -- netstat -tlnp` or equivalent commands. Identify any outbound connections to unusual ports.

3. Contain the threat:
   - Create an immediate NetworkPolicy named `quarantine-web-debug` in namespace `compromised-ns` that blocks ALL ingress and ALL egress from the pod `web-debug` (use label selector matching the pod's labels)
   - Do NOT delete the pod yet — it's needed for forensic analysis

4. Create a report file at `/root/incident-reports/compromised-ns-report.txt` containing:
   - Pod name and namespace
   - The suspicious process(es) found
   - Any suspicious network connections (IPs and ports)
   - The containment action taken (NetworkPolicy name and effect)

---

### Task 13 (6 points) — Medium
**Domain:** Supply Chain Security
**Context:** `kubectl config use-context enterprise-staging`
**Cluster:** Staging cluster

**Task:**
Multiple deployments in namespace `apps-staging` are using images with known vulnerabilities. Perform a supply chain remediation:

1. Use `trivy` to scan all unique images currently used by Deployments in the `apps-staging` namespace. Save a summary report of CRITICAL vulnerabilities to `/root/trivy-reports/apps-staging-summary.txt` in the format:
   ```
   IMAGE: <image-name> | CRITICAL: <count> | HIGH: <count>
   ```

2. The Deployment `api-service` is using image `registry.enterprise.internal/api:v2.0` which has a CRITICAL vulnerability in `openssl`. A patched image is available at `registry.enterprise.internal/api:v2.0.1`. Update the deployment to use the patched image.

3. The Deployment `worker-processor` is using image `nginx:1.19` from Docker Hub. This image is both outdated and from an unapproved registry. Update it to use `registry.enterprise.internal/nginx:1.27-hardened`.

4. Ensure both deployments roll out successfully with zero downtime (the deployments already have proper `strategy.rollingUpdate` configuration). Verify the new pods are running with the updated images.

---

### Task 14 (5 points) — Medium
**Domain:** Monitoring, Logging and Runtime Security
**Context:** `kubectl config use-context dmz-cluster`
**Cluster:** DMZ/edge cluster

**Task:**
Set up comprehensive audit logging and monitoring for the DMZ cluster:

1. Falco is running on the DMZ cluster. Create an additional Falco rule at `/etc/falco/rules.d/dmz-monitoring.yaml` on the control-plane node `cp-dmz` that triggers a **CRITICAL** alert when:
   - Any container in namespace `dmz-exposed` executes `kubectl`, `curl`, `wget`, or `nc` (netcat)
   - Output format: `"DMZ Alert: command=%proc.cmdline container=%container.name namespace=%k8s.ns.name user=%user.name image=%container.image.repository"`

2. Create a ConfigMap named `dmz-alert-config` in namespace `monitoring` containing a file `alert-rules.yaml` with the following content that defines the external webhook URL for Falco alerts:
   ```yaml
   webhook:
     url: "https://siem.enterprise.internal:9443/falco-alerts"
     minimumPriority: "warning"
     customHeaders:
       X-Source: "dmz-cluster"
       X-Environment: "production"
   ```

3. Ensure a ServiceAccount `falco-reader` exists in namespace `falco-system` with a Role that allows `get`, `list`, `watch` on `pods` and `events` in `falco-system` namespace only, bound via a RoleBinding `falco-reader-binding`.

---

### Task 15 (4 points) — Easy
**Domain:** Cluster Setup
**Context:** `kubectl config use-context enterprise-prod`
**Cluster:** Large production cluster

**Task:**
Configure network-level security for the `external-api` namespace:

1. Create a NetworkPolicy named `api-ingress-policy` in namespace `external-api` that:
   - Allows ingress to pods with label `role: api-server` on port 443 (TCP) from:
     - Any pod in the namespace `api-gateway` (namespace label: `kubernetes.io/metadata.name: api-gateway`)
     - The CIDR block `10.0.0.0/8` (internal network)
   - Denies all other ingress to those pods

2. Create a NetworkPolicy named `api-egress-policy` in namespace `external-api` that:
   - Allows egress from pods with label `role: api-server` to:
     - Pods with label `app: cache` in namespace `shared-services` on port 6379 (TCP)
     - DNS on port 53 (UDP and TCP) to any destination
     - The CIDR block `10.100.0.0/16` (database subnet) on port 5432 (TCP)
   - Denies all other egress from those pods

---

### Task 16 (5 points) — Hard
**Domain:** Minimize Microservice Vulnerabilities
**Context:** `kubectl config use-context enterprise-prod`
**Cluster:** Large production cluster

**Task:**
Implement a ValidatingAdmissionWebhook that enforces image source restrictions:

1. A webhook server is already running as a Deployment `image-validator` in namespace `admission-system`, exposed by Service `image-validator-svc` on port 443. The CA bundle for the webhook's TLS certificate is available at `/root/webhook-certs/ca.crt`.

2. Create a `ValidatingWebhookConfiguration` named `image-source-validator` with the following settings:
   - Webhook name: `validate-image-source.enterprise.internal`
   - Client config: service reference to `image-validator-svc` in `admission-system`, port 443, path `/validate`
   - CA bundle: content of `/root/webhook-certs/ca.crt` (base64-encoded)
   - Rules: intercept `CREATE` and `UPDATE` operations on `pods` in API version `v1` at scope `Namespaced`
   - `failurePolicy: Fail` (reject pods if webhook is unreachable)
   - `sideEffects: None`
   - `admissionReviewVersions: ["v1", "v1beta1"]`
   - `matchPolicy: Equivalent`
   - `namespaceSelector`: match only namespaces with label `image-validation: enabled`
   - `timeoutSeconds: 10`

3. Label the following namespaces with `image-validation: enabled`: `production`, `staging`, `payment-gateway`

4. Verify the webhook is working by attempting to create a test pod with an image from an unauthorized registry in the `production` namespace (expect rejection) and then clean up the test pod attempt.

---
---

## Mock Exam 4 — Solutions

---

### Solution 1
**Audit Policy + API Server Configuration**

**Step 1: Create the audit policy file**

SSH to the control-plane node:
```bash
ssh cp-prod
sudo mkdir -p /etc/kubernetes/audit
sudo mkdir -p /var/log/kubernetes/audit
```

Create `/etc/kubernetes/audit/policy.yaml`:
```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  # Rule 1: RequestResponse for everything in sensitive-apps namespace
  - level: RequestResponse
    namespaces: ["sensitive-apps"]
    resources:
      - group: ""
        resources: ["*"]
      - group: "*"
        resources: ["*"]

  # Rule 2: Request level for secrets, configmaps, tokenreviews in all namespaces
  - level: Request
    resources:
      - group: ""
        resources: ["secrets", "configmaps"]
      - group: "authentication.k8s.io"
        resources: ["tokenreviews"]

  # Rule 3: Metadata level for apps/v1 and batch/v1
  - level: Metadata
    resources:
      - group: "apps"
        resources: ["*"]
      - group: "batch"
        resources: ["*"]

  # Rule 4: None for health endpoints
  - level: None
    nonResourceURLs:
      - "/healthz*"
      - "/readyz*"
      - "/livez*"

  # Rule 5: Catch-all — Metadata for everything else
  - level: Metadata
```

**Step 2: Configure the API server**

Edit `/etc/kubernetes/manifests/kube-apiserver.yaml` and add the following flags to the command section:
```yaml
spec:
  containers:
  - command:
    - kube-apiserver
    # ... existing flags ...
    - --audit-policy-file=/etc/kubernetes/audit/policy.yaml
    - --audit-log-path=/var/log/kubernetes/audit/audit.log
    - --audit-log-maxsize=200
    - --audit-log-maxbackup=5
    - --audit-log-maxage=30
```

Add volume mounts:
```yaml
    volumeMounts:
    # ... existing mounts ...
    - mountPath: /etc/kubernetes/audit
      name: audit-policy
      readOnly: true
    - mountPath: /var/log/kubernetes/audit
      name: audit-log
```

Add volumes:
```yaml
  volumes:
  # ... existing volumes ...
  - name: audit-policy
    hostPath:
      path: /etc/kubernetes/audit
      type: DirectoryOrCreate
  - name: audit-log
    hostPath:
      path: /var/log/kubernetes/audit
      type: DirectoryOrCreate
```

**Fast approach:** Copy the exact YAML blocks above. Edit the manifest with `vi /etc/kubernetes/manifests/kube-apiserver.yaml`.

**Verification:**
```bash
# Wait for API server to restart
crictl ps | grep kube-apiserver
# Check audit log is being written
ls -la /var/log/kubernetes/audit/audit.log
tail -5 /var/log/kubernetes/audit/audit.log
# Check the log contains entries
cat /var/log/kubernetes/audit/audit.log | head -20
# Verify API server is healthy
kubectl get nodes
```

**Points breakdown:**
- Correct audit policy with all 5 rules in correct order: 4 points
- API server flags correct: 2 points
- Volume mounts and volumes correct: 1 point
- API server restarts and audit log is written: 1 point

---

### Solution 2
**Zero-Trust Namespace**

**Step 1: Create namespace with PSA labels**
```bash
kubectl create namespace payment-gateway
kubectl label namespace payment-gateway \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=v1.35 \
  pod-security.kubernetes.io/warn=restricted \
  pod-security.kubernetes.io/warn-version=v1.35 \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/audit-version=v1.35
```

**Step 2: Default-deny NetworkPolicy**
```yaml
# default-deny-all.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: payment-gateway
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

**Step 3: Selective allow NetworkPolicy**
```yaml
# allow-payment-flow.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-payment-flow
  namespace: payment-gateway
spec:
  podSelector:
    matchLabels:
      app: payment-api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: frontend
          podSelector:
            matchLabels:
              app: api-gateway
      ports:
        - protocol: TCP
          port: 8443
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: database
          podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
---
# DNS egress for all pods in namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: payment-gateway
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

Note: The DNS policy is separate because it applies to ALL pods in the namespace, while the payment-flow policy targets only `app: payment-api` pods. Alternatively, you can add the DNS egress rule to the `allow-payment-flow` policy's egress array — but then only `payment-api` pods would get DNS access. The task says "Allows all pods", so a separate policy is correct.

**Step 4: ResourceQuota**
```yaml
# payment-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: payment-quota
  namespace: payment-gateway
spec:
  hard:
    pods: "10"
    requests.cpu: "8"
    requests.memory: "16Gi"
    limits.cpu: "16"
    limits.memory: "32Gi"
    persistentvolumeclaims: "5"
    services.nodeports: "0"
```

**Step 5: LimitRange**
```yaml
# payment-limits.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: payment-limits
  namespace: payment-gateway
spec:
  limits:
    - type: Container
      default:
        cpu: "500m"
        memory: "512Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      max:
        cpu: "2"
        memory: "4Gi"
```

**Step 6: RBAC**
```yaml
# payment-developer-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: payment-developer
  namespace: payment-gateway
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["create", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: payment-dev-binding
  namespace: payment-gateway
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: payment-developer
subjects:
  - kind: Group
    name: payment-team
    apiGroup: rbac.authorization.k8s.io
```

Apply all:
```bash
kubectl apply -f default-deny-all.yaml
kubectl apply -f allow-payment-flow.yaml
kubectl apply -f payment-quota.yaml
kubectl apply -f payment-limits.yaml
kubectl apply -f payment-developer-role.yaml
```

**Fast approach:** Use `kubectl create` commands where possible:
```bash
kubectl create namespace payment-gateway
kubectl label ns payment-gateway pod-security.kubernetes.io/enforce=restricted pod-security.kubernetes.io/enforce-version=v1.35 pod-security.kubernetes.io/warn=restricted pod-security.kubernetes.io/warn-version=v1.35 pod-security.kubernetes.io/audit=restricted pod-security.kubernetes.io/audit-version=v1.35
kubectl create quota payment-quota -n payment-gateway --hard=pods=10,requests.cpu=8,requests.memory=16Gi,limits.cpu=16,limits.memory=32Gi,persistentvolumeclaims=5,services.nodeports=0
kubectl create role payment-developer -n payment-gateway --verb=get,list,watch --resource=pods,services,configmaps
# Then edit the role to add create/delete on pods or apply YAML
kubectl create rolebinding payment-dev-binding -n payment-gateway --role=payment-developer --group=payment-team
# NetworkPolicy, LimitRange must be done via YAML
```

**Verification:**
```bash
kubectl get ns payment-gateway --show-labels
kubectl get networkpolicy -n payment-gateway
kubectl get resourcequota -n payment-gateway
kubectl get limitrange -n payment-gateway
kubectl get role,rolebinding -n payment-gateway
kubectl describe quota payment-quota -n payment-gateway
```

**Points breakdown:**
- Namespace with correct PSA labels: 1 point
- Default-deny NetworkPolicy: 1 point
- Selective-allow NetworkPolicy with correct selectors: 2 points
- ResourceQuota with all fields: 1 point
- LimitRange: 1 point
- RBAC Role + RoleBinding: 1 point

---

### Solution 3
**Kyverno ClusterPolicy**

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: restrict-container-privileges
spec:
  validationFailureAction: Enforce
  background: true
  rules:
    # Rule 1: Block privileged containers
    - name: block-privileged
      match:
        any:
          - resources:
              kinds:
                - Pod
                - Deployment
                - StatefulSet
                - DaemonSet
                - Job
                - CronJob
      validate:
        message: "Privileged containers are not allowed. Set securityContext.privileged to false."
        pattern:
          spec:
            =(initContainers):
              - =(securityContext):
                  =(privileged): false
            containers:
              - =(securityContext):
                  =(privileged): false

    # Rule 2: Block host-level namespaces
    - name: block-host-networking
      match:
        any:
          - resources:
              kinds:
                - Pod
                - Deployment
                - StatefulSet
                - DaemonSet
                - Job
                - CronJob
      validate:
        message: "Host-level namespaces (hostNetwork, hostPID, hostIPC) are forbidden."
        pattern:
          spec:
            =(hostNetwork): false
            =(hostPID): false
            =(hostIPC): false

    # Rule 3: Require runAsNonRoot
    - name: require-non-root
      match:
        any:
          - resources:
              kinds:
                - Pod
                - Deployment
                - StatefulSet
                - DaemonSet
                - Job
                - CronJob
      validate:
        message: "All containers must set securityContext.runAsNonRoot to true."
        pattern:
          spec:
            =(initContainers):
              - securityContext:
                  runAsNonRoot: true
            containers:
              - securityContext:
                  runAsNonRoot: true

    # Rule 4: Restrict registries
    - name: restrict-registries
      match:
        any:
          - resources:
              kinds:
                - Pod
                - Deployment
                - StatefulSet
                - DaemonSet
                - Job
                - CronJob
      validate:
        message: "Images must come from approved registries only."
        foreach:
          - list: "request.object.spec.[initContainers, containers][]"
            deny:
              conditions:
                all:
                  - key: "{{ element.image }}"
                    operator: AnyNotIn
                    value:
                      - "registry.enterprise.internal/*"
                      - "docker.io/library/*"
                      - "gcr.io/enterprise-project/*"
```

Note: For Kyverno, the `foreach` with `deny` approach for image validation is more reliable. An alternative is using `validate.deny` with `conditions`. The key is that Kyverno auto-applies pod-level rules to controllers' pod templates when `background: true` is set and the controller kinds are included in `match`.

**Fast approach:** Write the YAML directly and `kubectl apply -f`.

**Verification:**
```bash
# Should be BLOCKED (nginx is from docker.io/library/ but without explicit prefix, 
# it resolves to docker.io/library/nginx — this MAY pass depending on Kyverno image normalization)
# To be safe, test with an explicitly non-approved image:
kubectl run test-blocked --image=quay.io/random/nginx:latest --dry-run=server

# Should succeed:
kubectl run test-allowed --image=registry.enterprise.internal/nginx:1.25 \
  --overrides='{"spec":{"containers":[{"name":"test-allowed","image":"registry.enterprise.internal/nginx:1.25","securityContext":{"runAsNonRoot":true,"allowPrivilegeEscalation":false}}]}}' \
  --dry-run=server

# Check policy status
kubectl get clusterpolicy restrict-container-privileges
```

**Points breakdown:**
- Rule block-privileged correct: 1.5 points
- Rule block-host-networking correct: 1.5 points
- Rule require-non-root correct: 1.5 points
- Rule restrict-registries correct: 1.5 points
- validationFailureAction: Enforce set: 0.5 points
- Verification attempts: 0.5 points

---

### Solution 4
**Custom Falco Rules**

SSH to each worker node (`worker-1` through `worker-5`) and create `/etc/falco/rules.d/custom-enterprise.yaml`:

```yaml
- rule: Unauthorized Package Manager Execution
  desc: Detect execution of package managers inside containers
  condition: >
    spawned_process and
    container and
    proc.name in (apt, apt-get, yum, dnf, apk, pip, pip3, npm)
  output: >
    CRITICAL: Package manager executed in container
    (timestamp=%evt.time container_id=%container.id container_name=%container.name
    user=%user.name command=%proc.cmdline parent=%proc.pname)
  priority: CRITICAL
  tags: [supply_chain, container]

- rule: Sensitive Mount Detected
  desc: Detect containers mounting sensitive host paths
  condition: >
    container and evt.type = mount and
    (mnt.source = "/etc/shadow" or
     mnt.source = "/etc/passwd" or
     mnt.source startswith "/root/.ssh" or
     mnt.source = "/var/run/docker.sock")
  output: >
    WARNING: Sensitive host path mounted in container
    (container=%container.name image=%container.image.repository
    mount_source=%mnt.source mount_dest=%mnt.dest)
  priority: WARNING
  tags: [filesystem, container]

- rule: Reverse Shell Detected
  desc: Detect reverse shell attempts in containers
  condition: >
    container and
    evt.type in (connect) and
    evt.dir = < and
    proc.name in (bash, sh, dash, zsh, csh) and
    fd.type = ipv4
  output: >
    EMERGENCY: Reverse shell detected in container
    (container=%container.name process=%proc.name user=%user.name
    connection=%fd.name ip=%fd.sip port=%fd.sport)
  priority: EMERGENCY
  tags: [network, mitre_execution]

- rule: Crypto Mining Indicator
  desc: Detect crypto mining activity in containers
  condition: >
    container and
    ((evt.type in (connect, sendto) and
      fd.sport in (3333, 4444, 5555, 8333, 9999, 14444, 14433)) or
     (spawned_process and
      proc.name in (xmrig, minerd, cpuminer, cgminer)))
  output: >
    CRITICAL: Crypto mining activity detected
    (container=%container.name process=%proc.name user=%user.name
    connection=%fd.name command=%proc.cmdline)
  priority: CRITICAL
  tags: [crypto, mitre_execution]
```

**Fast approach:** Create the file on one node, then `scp` to all others:
```bash
ssh worker-1
sudo vi /etc/falco/rules.d/custom-enterprise.yaml
# paste content
# then copy to other nodes
for node in worker-2 worker-3 worker-4 worker-5; do
  scp /etc/falco/rules.d/custom-enterprise.yaml $node:/etc/falco/rules.d/
done
```

Restart Falco DaemonSet:
```bash
kubectl rollout restart daemonset falco -n falco-system
```

**Verification:**
```bash
kubectl rollout status daemonset falco -n falco-system
# Check Falco logs for rule loading
kubectl logs -n falco-system -l app=falco --tail=50 | grep -i "rule"
# Look for "Loaded rules" message
kubectl logs -n falco-system -l app=falco --tail=20 | grep -i "custom-enterprise"
```

**Points breakdown:**
- Package manager rule correct: 1.5 points
- Sensitive mount rule correct: 1.5 points
- Reverse shell rule correct: 1.5 points
- Crypto mining rule correct: 1.5 points
- Rules deployed to all nodes: 0.5 points
- Falco restarted and rules loaded: 0.5 points

---

### Solution 5
**ServiceAccount Hardening**

**Step 1: Fix metrics-collector permissions**
```bash
# Create the least-privilege ClusterRole
kubectl create clusterrole metrics-reader \
  --verb=get,list,watch \
  --resource=pods,nodes,services,endpoints

# Also add metrics resources (can't do this via kubectl create, so patch or apply YAML)
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: metrics-reader
rules:
  - apiGroups: [""]
    resources: ["pods", "nodes", "services", "endpoints"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["metrics.k8s.io"]
    resources: ["pods", "nodes"]
    verbs: ["get", "list", "watch"]
EOF

# Update the ClusterRoleBinding
kubectl edit clusterrolebinding metrics-full-access
# Change roleRef.name from cluster-admin to metrics-reader
```

Note: `roleRef` is immutable — you cannot edit it. You must delete and recreate:
```bash
kubectl delete clusterrolebinding metrics-full-access
kubectl create clusterrolebinding metrics-full-access \
  --clusterrole=metrics-reader \
  --serviceaccount=monitoring:metrics-collector
```

**Step 2: Fix deploy-bot token mounting**
```bash
# Patch the ServiceAccount
kubectl patch serviceaccount deploy-bot -n ci-cd \
  -p '{"automountServiceAccountToken": false}'

# Patch the Deployment to explicitly mount the token
kubectl patch deployment deploy-runner -n ci-cd \
  --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/automountServiceAccountToken","value":true}]'
```

**Step 3: Delete orphaned SA token secrets**
```bash
# List all SA token secrets in legacy-apps
kubectl get secrets -n legacy-apps --field-selector type=kubernetes.io/service-account-token

# For each secret, check if it's mounted by any pod
for secret in $(kubectl get secrets -n legacy-apps --field-selector type=kubernetes.io/service-account-token -o jsonpath='{.items[*].metadata.name}'); do
  used=$(kubectl get pods -n legacy-apps -o json | grep -c "$secret" || true)
  if [ "$used" -eq 0 ]; then
    echo "Orphaned: $secret"
    kubectl delete secret "$secret" -n legacy-apps
  fi
done
```

**Fast approach:** Steps above are already fairly fast. Key insight: `roleRef` in ClusterRoleBindings is immutable, so you must delete + recreate.

**Verification:**
```bash
kubectl describe clusterrolebinding metrics-full-access
kubectl get sa deploy-bot -n ci-cd -o yaml | grep automount
kubectl get deployment deploy-runner -n ci-cd -o yaml | grep automount
kubectl get secrets -n legacy-apps --field-selector type=kubernetes.io/service-account-token
```

**Points breakdown:**
- New ClusterRole metrics-reader with correct permissions: 2 points
- ClusterRoleBinding updated (delete+recreate): 1 point
- ServiceAccount token mount disabled + deployment override: 2 points
- Orphaned secrets identified and deleted: 1 point

---

### Solution 6
**Combined AppArmor + Seccomp + Sysctl Hardening**

**Step 1: AppArmor profile (on infra-node)**
```bash
ssh infra-node
sudo cat > /etc/apparmor.d/k8s-restricted-profile << 'EOF'
#include <tunables/global>

profile k8s-restricted-profile flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # Allow network TCP and UDP
  network inet stream,
  network inet dgram,

  # Deny raw network access
  deny network raw,

  # Deny mount
  deny mount,

  # Allow read of specific files
  /etc/hostname r,
  /etc/resolv.conf r,
  /etc/hosts r,

  # Allow writes only to /tmp and /var/log/app
  /tmp/** rw,
  /var/log/app/** rw,

  # Deny all other file writes
  deny /** w,

  # Allow read of everything else (needed for binary execution)
  /** r,
  /** ix,
}
EOF

sudo apparmor_parser -r /etc/apparmor.d/k8s-restricted-profile
sudo apparmor_status | grep k8s-restricted-profile
```

**Step 2: Seccomp profile (on infra-node)**
```bash
sudo mkdir -p /var/lib/kubelet/seccomp/profiles
sudo cat > /var/lib/kubelet/seccomp/profiles/restricted-syscalls.json << 'SECCOMP_EOF'
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": [
    "SCMP_ARCH_X86_64",
    "SCMP_ARCH_X86",
    "SCMP_ARCH_AARCH64"
  ],
  "syscalls": [
    {
      "names": [
        "read", "write", "open", "close", "stat", "fstat", "lstat",
        "poll", "lseek", "mmap", "mprotect", "munmap", "brk",
        "rt_sigaction", "rt_sigprocmask", "rt_sigreturn",
        "ioctl", "access", "pipe", "select", "sched_yield",
        "mremap", "msync", "mincore", "madvise",
        "dup", "dup2", "pause", "nanosleep",
        "getpid", "socket", "connect", "accept", "sendto", "recvfrom",
        "bind", "listen", "clone", "execve", "exit", "wait4", "kill",
        "uname", "fcntl", "flock", "fsync", "ftruncate",
        "getcwd", "chdir", "mkdir", "rmdir", "link", "unlink", "readlink",
        "chmod", "chown", "gettimeofday",
        "getuid", "getgid", "geteuid", "getegid", "getppid", "getpgrp",
        "setpgid", "getrlimit", "getrusage", "sysinfo", "times",
        "futex", "set_tid_address", "clock_gettime", "clock_getres",
        "exit_group", "epoll_create", "epoll_ctl", "epoll_wait",
        "openat", "mkdirat", "newfstatat", "unlinkat", "renameat",
        "readlinkat", "fchmodat", "faccessat",
        "set_robust_list", "arch_prctl", "prlimit64", "getrandom",
        "close_range", "rseq"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
SECCOMP_EOF
```

**Step 3: Create the hardened pod (back on the cluster)**
```bash
# Switch context back
kubectl config use-context enterprise-prod
kubectl create namespace secure-runtime --dry-run=client -o yaml | kubectl apply -f -
```

```yaml
# hardened-workload.yaml
apiVersion: v1
kind: Pod
metadata:
  name: hardened-workload
  namespace: secure-runtime
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 1000
    runAsNonRoot: true
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/restricted-syscalls.json
    sysctls:
      - name: net.ipv4.ip_unprivileged_port_start
        value: "1024"
      - name: net.ipv4.tcp_syncookies
        value: "1"
    appArmorProfile:
      type: Localhost
      localhostProfile: k8s-restricted-profile
  containers:
    - name: app
      image: registry.enterprise.internal/app:v2.1
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop:
            - ALL
```

```bash
kubectl apply -f hardened-workload.yaml
```

Note: In Kubernetes v1.30+, AppArmor uses the `spec.securityContext.appArmorProfile` field (GA) instead of the old annotation-based approach. The `Localhost` type references profiles loaded on the node.

**Fast approach:** Have the YAML ready. The AppArmor profile and Seccomp JSON are the time-consuming parts — type carefully.

**Verification:**
```bash
# Verify AppArmor profile is loaded on the node
ssh infra-node
sudo apparmor_status | grep k8s-restricted
exit

# Verify pod is running
kubectl get pod hardened-workload -n secure-runtime
kubectl describe pod hardened-workload -n secure-runtime | grep -A5 "Security Context"

# Check seccomp and apparmor are applied
kubectl get pod hardened-workload -n secure-runtime -o jsonpath='{.spec.securityContext.seccompProfile}'
kubectl get pod hardened-workload -n secure-runtime -o jsonpath='{.spec.securityContext.appArmorProfile}'
```

**Points breakdown:**
- AppArmor profile created and loaded: 2 points
- Seccomp profile with correct syscalls: 2 points
- Pod with all three mechanisms (AppArmor, Seccomp, sysctl): 2 points
- Pod runs as non-root with dropped capabilities: 1 point

---

### Solution 7
**CIS Benchmark Remediation**

SSH to the control-plane node:
```bash
ssh cp-dmz
```

Edit `/etc/kubernetes/manifests/kube-apiserver.yaml`:

**Fix 1: Disable anonymous auth**
```yaml
# Add or change:
- --anonymous-auth=false
```

**Fix 2: Set kubelet certificate authority**
```yaml
# Add:
- --kubelet-certificate-authority=/etc/kubernetes/pki/ca.crt
```

**Fix 3: Fix authorization mode**
```yaml
# Change from:
- --authorization-mode=AlwaysAllow
# To:
- --authorization-mode=Node,RBAC
```

**Fix 4: Configure etcd peer TLS**

Edit `/etc/kubernetes/manifests/etcd.yaml`:
```yaml
# Add or verify these flags:
- --peer-cert-file=/etc/kubernetes/pki/etcd/peer.crt
- --peer-key-file=/etc/kubernetes/pki/etcd/peer.key
- --peer-trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt
- --peer-client-cert-auth=true
```

**Fast approach:** Use `sed` for quick edits:
```bash
sudo sed -i 's/--anonymous-auth=true/--anonymous-auth=false/' /etc/kubernetes/manifests/kube-apiserver.yaml
sudo sed -i 's/--authorization-mode=AlwaysAllow/--authorization-mode=Node,RBAC/' /etc/kubernetes/manifests/kube-apiserver.yaml
# For adding new flags, use vi — sed for additions is error-prone in YAML
```

**Verification:**
```bash
# Wait for components to restart
sleep 30
crictl ps | grep -E "kube-apiserver|etcd"
# Test cluster connectivity
kubectl --kubeconfig=/etc/kubernetes/admin.conf get nodes
# Verify settings
kubectl --kubeconfig=/etc/kubernetes/admin.conf -v=8 get nodes 2>&1 | head -5
# Check anonymous auth is disabled
curl -k https://localhost:6443/api/v1/namespaces --header "Authorization: Bearer invalid" 2>/dev/null | head -5
```

**Points breakdown:**
- Anonymous auth disabled: 1.5 points
- Kubelet CA configured: 1.5 points
- Authorization mode fixed: 2 points
- etcd peer TLS configured: 2 points

---

### Solution 8
**Image Supply Chain Security**

**Step 1: Scan image with Trivy**
```bash
mkdir -p /root/trivy-reports
/usr/local/bin/trivy image --format json \
  --output /root/trivy-reports/webapp-v3.2.json \
  registry.enterprise.internal/webapp:v3.2
```

**Step 2: Update Dockerfile**
```bash
vi /root/dockerfiles/webapp/Dockerfile
```

Change the Dockerfile:
```dockerfile
# Change FROM line
FROM ubuntu:24.04

# Add security update layer
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# ... rest of existing Dockerfile layers ...

# Add before CMD (if not already present)
USER 1001

CMD ["./app"]
```

**Step 3: Configure ImagePolicyWebhook**

Create `/etc/kubernetes/admission/admission-config.yaml`:
```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
  - name: ImagePolicyWebhook
    configuration:
      imagePolicy:
        kubeConfigFile: /etc/kubernetes/admission/image-policy-config.yaml
        allowTTL: 50
        denyTTL: 50
        retryBackoff: 500
        defaultAllow: false
```

Edit `/etc/kubernetes/manifests/kube-apiserver.yaml`:
```yaml
# Add ImagePolicyWebhook to the enable-admission-plugins flag:
- --enable-admission-plugins=NodeRestriction,ImagePolicyWebhook
# Add the admission control config:
- --admission-control-config-file=/etc/kubernetes/admission/admission-config.yaml
```

Add volume mount for the admission directory:
```yaml
    volumeMounts:
    - mountPath: /etc/kubernetes/admission
      name: admission-config
      readOnly: true
  volumes:
  - name: admission-config
    hostPath:
      path: /etc/kubernetes/admission
      type: DirectoryOrCreate
```

**Fast approach:** Steps above are sequential by necessity. Focus on getting the admission-config.yaml syntax right — a common exam pitfall.

**Verification:**
```bash
# Check Trivy report
cat /root/trivy-reports/webapp-v3.2.json | python3 -m json.tool | head -30

# Check Dockerfile changes
cat /root/dockerfiles/webapp/Dockerfile

# Wait for API server restart and verify
sleep 30
crictl ps | grep kube-apiserver
kubectl get nodes
```

**Points breakdown:**
- Trivy scan completed and saved: 1 point
- Dockerfile updated (base image + upgrade + USER): 2 points
- AdmissionConfiguration file correct: 2 points
- API server flags and volumes correct: 1.5 points
- API server restarts successfully: 0.5 points

---

### Solution 9
**Certificate-Based Security**

**Step 1: Create CertificateSigningRequest**
```bash
# Read the CSR file and base64 encode it
CSR_CONTENT=$(cat /root/certs/security-auditor.csr | base64 | tr -d '\n')

cat <<EOF | kubectl apply -f -
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: security-auditor-csr
spec:
  request: ${CSR_CONTENT}
  signerName: kubernetes.io/kube-apiserver-client
  expirationSeconds: 86400
  usages:
    - digital signature
    - key encipherment
    - client auth
EOF
```

**Step 2: Approve the CSR**
```bash
kubectl certificate approve security-auditor-csr
```

**Step 3: Extract the certificate**
```bash
kubectl get csr security-auditor-csr -o jsonpath='{.status.certificate}' | base64 -d > /root/certs/security-auditor.crt
```

**Step 4: Create the ClusterRole**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: security-audit-role
rules:
  - apiGroups: ["", "apps", "batch"]
    resources: ["pods", "services", "deployments", "replicasets", "statefulsets", "daemonsets", "jobs", "cronjobs"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["networking.k8s.io"]
    resources: ["networkpolicies", "ingresses"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["rbac.authorization.k8s.io"]
    resources: ["roles", "rolebindings", "clusterroles", "clusterrolebindings"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get", "list"]
```

**Step 5: Create the ClusterRoleBinding**
```bash
kubectl create clusterrolebinding security-auditor-binding \
  --clusterrole=security-audit-role \
  --user=security-auditor
```

**Fast approach:**
```bash
# One-liner for CSR
cat /root/certs/security-auditor.csr | base64 | tr -d '\n' | xargs -I{} kubectl apply -f - <<EOF
# ... (not practical as one-liner, use the YAML approach)
EOF

# Quick ClusterRole
kubectl create clusterrole security-audit-role \
  --verb=get,list,watch \
  --resource=pods,services,deployments,replicasets,statefulsets,daemonsets,jobs,cronjobs,networkpolicies,ingresses,roles,rolebindings,clusterroles,clusterrolebindings
# Then edit to add the secrets exception (get,list only, no watch)
kubectl edit clusterrole security-audit-role
```

**Verification:**
```bash
kubectl get csr security-auditor-csr
cat /root/certs/security-auditor.crt | openssl x509 -noout -subject
kubectl describe clusterrole security-audit-role
kubectl describe clusterrolebinding security-auditor-binding
# Test access
kubectl auth can-i get pods --as=security-auditor
kubectl auth can-i watch secrets --as=security-auditor  # Should be "no"
kubectl auth can-i get secrets --as=security-auditor     # Should be "yes"
```

**Points breakdown:**
- CSR created with correct fields: 1.5 points
- CSR approved and certificate extracted: 1 point
- ClusterRole with correct permissions (especially secrets get/list but no watch): 2 points
- ClusterRoleBinding correct: 1 point
- Verification of can-i results: 0.5 points

---

### Solution 10
**Encryption at Rest + etcd Backup**

**Step 1: Generate the encryption key**
```bash
ssh cp-prod
echo -n "k8s-encryption-key-2026-prod-001" | base64
# Result: azhzLWVuY3J5cHRpb24ta2V5LTIwMjYtcHJvZC0wMDE=
```

**Step 2: Create EncryptionConfiguration**
```bash
sudo mkdir -p /etc/kubernetes/encryption
sudo cat > /etc/kubernetes/encryption/config.yaml << 'EOF'
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: secret-key-1
              secret: azhzLWVuY3J5cHRpb24ta2V5LTIwMjYtcHJvZC0wMDE=
      - identity: {}
  - resources:
      - configmaps
    providers:
      - aesgcm:
          keys:
            - name: configmap-key-1
              secret: azhzLWVuY3J5cHRpb24ta2V5LTIwMjYtcHJvZC0wMDE=
      - identity: {}
EOF
```

**Step 3: Configure API server**

Edit `/etc/kubernetes/manifests/kube-apiserver.yaml`:
```yaml
spec:
  containers:
  - command:
    - kube-apiserver
    # Add:
    - --encryption-provider-config=/etc/kubernetes/encryption/config.yaml

    volumeMounts:
    # Add:
    - mountPath: /etc/kubernetes/encryption
      name: encryption-config
      readOnly: true

  volumes:
  # Add:
  - name: encryption-config
    hostPath:
      path: /etc/kubernetes/encryption
      type: DirectoryOrCreate
```

**Step 4: Re-encrypt existing secrets**
```bash
# Wait for API server to restart
sleep 30
kubectl get secrets -n default -o json | kubectl replace -f -
```

**Step 5: Backup etcd**
```bash
sudo mkdir -p /root/etcd-backups
ETCDCTL_API=3 etcdctl snapshot save /root/etcd-backups/snapshot-$(date +%Y%m%d).db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

**Step 6: Verify snapshot**
```bash
ETCDCTL_API=3 etcdutl snapshot status /root/etcd-backups/snapshot-$(date +%Y%m%d).db --write-out=table
```

**Fast approach:** Have the EncryptionConfiguration YAML ready to paste. The key gotcha is correctly base64-encoding the key and matching the provider type (aescbc vs aesgcm) per resource type.

**Verification:**
```bash
# Check API server is using encryption
ps aux | grep encryption-provider-config

# Verify a secret is encrypted in etcd
ETCDCTL_API=3 etcdctl get /registry/secrets/default/$(kubectl get secrets -n default -o jsonpath='{.items[0].metadata.name}') \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key | hexdump -C | head -10
# Should show "k8s:enc:aescbc:v1:secret-key-1" prefix, not plaintext

# Verify snapshot
etcdutl snapshot status /root/etcd-backups/snapshot-*.db --write-out=table
```

**Points breakdown:**
- EncryptionConfiguration correct (two resource blocks, correct providers): 2 points
- API server configured with volume mount: 1 point
- Re-encryption of existing secrets: 1 point
- etcd backup created with correct certs: 1.5 points
- Snapshot verification: 0.5 points

---

### Solution 11
**RuntimeClass with gVisor**

**Step 1: Create RuntimeClass**
```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor-sandbox
handler: runsc
scheduling:
  nodeSelector:
    runtime: gvisor
```

```bash
kubectl apply -f runtimeclass.yaml
```

**Step 2: Create namespace and Deployment**
```bash
kubectl create namespace sandbox-workloads
```

```yaml
# sandboxed-app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sandboxed-app
  namespace: sandbox-workloads
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sandboxed-app
  template:
    metadata:
      labels:
        app: sandboxed-app
    spec:
      runtimeClassName: gvisor-sandbox
      securityContext:
        runAsNonRoot: true
        runAsUser: 65534
        runAsGroup: 65534
        fsGroup: 65534
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: microservice
          image: registry.enterprise.internal/microservice:v1.4
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
```

```bash
kubectl apply -f sandboxed-app.yaml
```

**Fast approach:** The YAML above is the fastest correct approach. No shortcuts for this one — the full spec is needed.

**Verification:**
```bash
kubectl get runtimeclass gvisor-sandbox
kubectl get deployment sandboxed-app -n sandbox-workloads
kubectl get pods -n sandbox-workloads -o wide
# Verify runtimeClassName
kubectl get pods -n sandbox-workloads -o jsonpath='{.items[*].spec.runtimeClassName}'
# Verify pods are on gvisor nodes
kubectl get pods -n sandbox-workloads -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.nodeName}{"\n"}{end}'
# Check node labels
kubectl get nodes -l runtime=gvisor
```

**Points breakdown:**
- RuntimeClass created with correct handler and scheduling: 2 points
- Deployment with correct RuntimeClass reference: 1 point
- Security contexts (pod-level and container-level) correct: 2 points
- Pods running on correct nodes: 1 point

---

### Solution 12
**Incident Response**

**Step 1: Investigate pods**
```bash
kubectl get pods -n compromised-ns -o wide

# Check security contexts
kubectl get pods -n compromised-ns -o jsonpath='{range .items[*]}{.metadata.name}: privileged={.spec.containers[0].securityContext.privileged}, runAsUser={.spec.containers[0].securityContext.runAsUser}{"\n"}{end}'

# Check processes in each pod
for pod in $(kubectl get pods -n compromised-ns -o jsonpath='{.items[*].metadata.name}'); do
  echo "=== $pod ==="
  kubectl exec $pod -n compromised-ns -- ps aux 2>/dev/null || echo "ps not available"
done
```

**Step 2: Examine web-debug specifically**
```bash
# Check running processes
kubectl exec web-debug -n compromised-ns -- ps aux

# Check network connections
kubectl exec web-debug -n compromised-ns -- netstat -tlnp 2>/dev/null || \
kubectl exec web-debug -n compromised-ns -- ss -tlnp 2>/dev/null || \
kubectl exec web-debug -n compromised-ns -- cat /proc/net/tcp

# Check for suspicious files
kubectl exec web-debug -n compromised-ns -- find /tmp -type f 2>/dev/null
```

**Step 3: Quarantine the pod**
```bash
# Get the pod's labels
kubectl get pod web-debug -n compromised-ns --show-labels

# Create quarantine NetworkPolicy
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: quarantine-web-debug
  namespace: compromised-ns
spec:
  podSelector:
    matchLabels:
      app: web-debug  # Use actual labels from the pod
  policyTypes:
    - Ingress
    - Egress
EOF
```

**Step 4: Create incident report**
```bash
mkdir -p /root/incident-reports
cat > /root/incident-reports/compromised-ns-report.txt << 'EOF'
INCIDENT REPORT
===============
Date: $(date)
Namespace: compromised-ns

AFFECTED POD:
- Pod Name: web-debug
- Namespace: compromised-ns

SUSPICIOUS PROCESSES:
- [List processes found from ps aux output, e.g., xmrig, reverse shell, etc.]

SUSPICIOUS NETWORK CONNECTIONS:
- [List connections found from netstat, e.g., outbound to IP:PORT]

CONTAINMENT ACTIONS:
- Applied NetworkPolicy "quarantine-web-debug" in namespace "compromised-ns"
- Effect: Blocks ALL ingress and ALL egress traffic to/from pod web-debug
- Pod preserved for forensic analysis (not deleted)

STATUS: Contained — awaiting forensic investigation
EOF
```

**Fast approach:** Run investigation commands in parallel terminals if possible. The quarantine NetworkPolicy is the critical action.

**Verification:**
```bash
kubectl get networkpolicy quarantine-web-debug -n compromised-ns
kubectl describe networkpolicy quarantine-web-debug -n compromised-ns
# Verify network is blocked
kubectl exec web-debug -n compromised-ns -- wget --timeout=3 -O- http://google.com 2>&1 || echo "Network blocked (expected)"
cat /root/incident-reports/compromised-ns-report.txt
```

**Points breakdown:**
- Correctly identified suspicious pods: 1.5 points
- Network connections examined: 1 point
- Quarantine NetworkPolicy applied correctly: 2 points
- Incident report created with required information: 1.5 points

---

### Solution 13
**Supply Chain Remediation**

**Step 1: Scan all images**
```bash
mkdir -p /root/trivy-reports

# Get all unique images from deployments in apps-staging
IMAGES=$(kubectl get deployments -n apps-staging -o jsonpath='{range .items[*]}{range .spec.template.spec.containers[*]}{.image}{"\n"}{end}{end}' | sort -u)

# Scan each image and create summary
> /root/trivy-reports/apps-staging-summary.txt
for img in $IMAGES; do
  RESULT=$(/usr/local/bin/trivy image --severity CRITICAL,HIGH --format json "$img" 2>/dev/null)
  CRITICAL=$(echo "$RESULT" | jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length')
  HIGH=$(echo "$RESULT" | jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH")] | length')
  echo "IMAGE: $img | CRITICAL: $CRITICAL | HIGH: $HIGH" >> /root/trivy-reports/apps-staging-summary.txt
done

cat /root/trivy-reports/apps-staging-summary.txt
```

**Step 2: Update api-service deployment**
```bash
kubectl set image deployment/api-service \
  api-service=registry.enterprise.internal/api:v2.0.1 \
  -n apps-staging
```

Note: The container name might differ. Check first:
```bash
kubectl get deployment api-service -n apps-staging -o jsonpath='{.spec.template.spec.containers[*].name}'
# Use the actual container name in the set image command
```

**Step 3: Update worker-processor deployment**
```bash
kubectl set image deployment/worker-processor \
  worker-processor=registry.enterprise.internal/nginx:1.27-hardened \
  -n apps-staging
```

**Step 4: Verify rollout**
```bash
kubectl rollout status deployment/api-service -n apps-staging
kubectl rollout status deployment/worker-processor -n apps-staging
kubectl get pods -n apps-staging -o wide
# Verify images
kubectl get pods -n apps-staging -o jsonpath='{range .items[*]}{.metadata.name}: {.spec.containers[*].image}{"\n"}{end}'
```

**Fast approach:** `kubectl set image` is the fastest approach. Avoid editing the deployment YAML directly.

**Verification:**
```bash
cat /root/trivy-reports/apps-staging-summary.txt
kubectl get deployment api-service -n apps-staging -o jsonpath='{.spec.template.spec.containers[0].image}'
kubectl get deployment worker-processor -n apps-staging -o jsonpath='{.spec.template.spec.containers[0].image}'
kubectl get pods -n apps-staging
```

**Points breakdown:**
- Image scan and summary report: 2 points
- api-service updated to patched image: 1.5 points
- worker-processor updated to approved registry image: 1.5 points
- Both rollouts successful: 1 point

---

### Solution 14
**DMZ Audit and Monitoring**

**Step 1: Create Falco rule**

SSH to `cp-dmz`:
```bash
ssh cp-dmz
sudo mkdir -p /etc/falco/rules.d
sudo cat > /etc/falco/rules.d/dmz-monitoring.yaml << 'EOF'
- rule: DMZ Suspicious Command Execution
  desc: Detect execution of recon/exfil tools in DMZ namespace
  condition: >
    spawned_process and
    container and
    k8s.ns.name = "dmz-exposed" and
    proc.name in (kubectl, curl, wget, nc)
  output: >
    DMZ Alert: command=%proc.cmdline container=%container.name
    namespace=%k8s.ns.name user=%user.name
    image=%container.image.repository
  priority: CRITICAL
  tags: [dmz, network, mitre_discovery]
EOF
```

Restart Falco if it's running as a system service on this node:
```bash
sudo systemctl restart falco
# Or if it's a DaemonSet, restart from kubectl
```

**Step 2: Create ConfigMap**
```bash
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: dmz-alert-config
  namespace: monitoring
data:
  alert-rules.yaml: |
    webhook:
      url: "https://siem.enterprise.internal:9443/falco-alerts"
      minimumPriority: "warning"
      customHeaders:
        X-Source: "dmz-cluster"
        X-Environment: "production"
EOF
```

**Step 3: ServiceAccount, Role, and RoleBinding**
```bash
# Create ServiceAccount
kubectl create serviceaccount falco-reader -n falco-system

# Create Role
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: falco-reader-role
  namespace: falco-system
rules:
  - apiGroups: [""]
    resources: ["pods", "events"]
    verbs: ["get", "list", "watch"]
EOF

# Create RoleBinding
kubectl create rolebinding falco-reader-binding \
  -n falco-system \
  --role=falco-reader-role \
  --serviceaccount=falco-system:falco-reader
```

**Fast approach:**
```bash
kubectl create sa falco-reader -n falco-system
kubectl create role falco-reader-role -n falco-system --verb=get,list,watch --resource=pods,events
kubectl create rolebinding falco-reader-binding -n falco-system --role=falco-reader-role --serviceaccount=falco-system:falco-reader
```

**Verification:**
```bash
# Check Falco rules
ssh cp-dmz
cat /etc/falco/rules.d/dmz-monitoring.yaml
exit

# Check ConfigMap
kubectl get configmap dmz-alert-config -n monitoring -o yaml

# Check RBAC
kubectl get sa falco-reader -n falco-system
kubectl get role falco-reader-role -n falco-system
kubectl get rolebinding falco-reader-binding -n falco-system
kubectl auth can-i get pods -n falco-system --as=system:serviceaccount:falco-system:falco-reader
```

**Points breakdown:**
- Falco rule created with correct condition and output: 2 points
- ConfigMap with correct content: 1 point
- ServiceAccount + Role + RoleBinding correct: 2 points

---

### Solution 15
**NetworkPolicy for External API**

**Step 1: Ingress NetworkPolicy**
```yaml
# api-ingress-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-ingress-policy
  namespace: external-api
spec:
  podSelector:
    matchLabels:
      role: api-server
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: api-gateway
        - ipBlock:
            cidr: 10.0.0.0/8
      ports:
        - protocol: TCP
          port: 443
```

**Step 2: Egress NetworkPolicy**
```yaml
# api-egress-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-egress-policy
  namespace: external-api
spec:
  podSelector:
    matchLabels:
      role: api-server
  policyTypes:
    - Egress
  egress:
    # Rule 1: Allow to cache service
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: shared-services
          podSelector:
            matchLabels:
              app: cache
      ports:
        - protocol: TCP
          port: 6379
    # Rule 2: Allow DNS
    - to: []
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
    # Rule 3: Allow to database subnet
    - to:
        - ipBlock:
            cidr: 10.100.0.0/16
      ports:
        - protocol: TCP
          port: 5432
```

```bash
kubectl apply -f api-ingress-policy.yaml
kubectl apply -f api-egress-policy.yaml
```

**Fast approach:** Apply both YAML files directly. No kubectl shortcut for NetworkPolicy creation.

**Verification:**
```bash
kubectl get networkpolicy -n external-api
kubectl describe networkpolicy api-ingress-policy -n external-api
kubectl describe networkpolicy api-egress-policy -n external-api
```

**Points breakdown:**
- Ingress policy with correct selectors and port: 2 points
- Egress policy to cache with namespace+pod selector: 1 point
- DNS egress rule: 0.5 points
- Database subnet egress with CIDR and port: 0.5 points

---

### Solution 16
**ValidatingAdmissionWebhook**

**Step 1: Get CA bundle**
```bash
CA_BUNDLE=$(cat /root/webhook-certs/ca.crt | base64 | tr -d '\n')
```

**Step 2: Create ValidatingWebhookConfiguration**
```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: image-source-validator
webhooks:
  - name: validate-image-source.enterprise.internal
    clientConfig:
      service:
        name: image-validator-svc
        namespace: admission-system
        port: 443
        path: /validate
      caBundle: <BASE64_CA_BUNDLE>
    rules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
        scope: Namespaced
    failurePolicy: Fail
    sideEffects: None
    admissionReviewVersions: ["v1", "v1beta1"]
    matchPolicy: Equivalent
    namespaceSelector:
      matchLabels:
        image-validation: enabled
    timeoutSeconds: 10
```

Apply with the actual CA bundle:
```bash
cat <<EOF | sed "s|<BASE64_CA_BUNDLE>|${CA_BUNDLE}|" | kubectl apply -f -
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: image-source-validator
webhooks:
  - name: validate-image-source.enterprise.internal
    clientConfig:
      service:
        name: image-validator-svc
        namespace: admission-system
        port: 443
        path: /validate
      caBundle: <BASE64_CA_BUNDLE>
    rules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
        scope: Namespaced
    failurePolicy: Fail
    sideEffects: None
    admissionReviewVersions: ["v1", "v1beta1"]
    matchPolicy: Equivalent
    namespaceSelector:
      matchLabels:
        image-validation: enabled
    timeoutSeconds: 10
EOF
```

**Step 3: Label namespaces**
```bash
kubectl label namespace production image-validation=enabled
kubectl label namespace staging image-validation=enabled
kubectl label namespace payment-gateway image-validation=enabled
```

**Step 4: Verify**
```bash
# Test with unauthorized image (should be rejected)
kubectl run test-unauthorized --image=quay.io/malicious/app:latest -n production --dry-run=server
# Expected: Error from server (Forbidden): ...

# Clean up if the test pod somehow got created
kubectl delete pod test-unauthorized -n production --ignore-not-found
```

**Fast approach:** Use a heredoc with variable substitution for the CA bundle. The `sed` approach above handles the variable replacement cleanly.

**Verification:**
```bash
kubectl get validatingwebhookconfiguration image-source-validator
kubectl describe validatingwebhookconfiguration image-source-validator
kubectl get ns production staging payment-gateway --show-labels | grep image-validation
# Test rejection
kubectl run test-bad --image=unauthorized-registry.io/app:v1 -n production 2>&1
```

**Points breakdown:**
- ValidatingWebhookConfiguration with all correct fields: 2 points
- CA bundle correctly encoded and set: 1 point
- Namespaces labeled: 1 point
- Verification (test rejection): 1 point

---

## Mock Exam 4 — Scoring Guide

### Points Distribution by Domain

| Domain | Tasks | Points | % of Exam |
|--------|-------|--------|-----------|
| Cluster Setup | 1, 7, 15 | 8 + 7 + 4 = 19 | 19% |
| Cluster Hardening | 5, 9 | 6 + 6 = 12 | 12% |
| System Hardening | 6 | 7 | 7% |
| Minimize Microservice Vulnerabilities | 2, 10, 11, 16 | 8 + 7 + 6 + 5 = 26 | 26% |
| Supply Chain Security | 3, 8, 13 | 7 + 7 + 6 = 20 | 20% |
| Monitoring, Logging and Runtime Security | 4, 12, 14 | 7 + 6 + 5 = 18 | 18% |

### Difficulty Distribution

| Difficulty | Count | Points |
|------------|-------|--------|
| Easy | 1 (Task 15) | 4 |
| Medium | 6 (Tasks 5, 7, 9, 11, 12, 13) | 36 |
| Hard | 9 (Tasks 1, 2, 3, 4, 6, 8, 10, 14, 16) | 60 |
| **Total** | **16** | **100** |

### Score Interpretation

| Score | Assessment |
|-------|------------|
| 90–100 | Outstanding — You are over-prepared for the CKS exam |
| 80–89 | Excellent — You will pass the real exam comfortably |
| 67–79 | Passing — You're ready for the real exam |
| 55–66 | Almost there — Review your weak areas and retake in 1 week |
| 40–54 | Needs work — Significant gaps remain; focus on the domains you missed |
| Below 40 | Not ready — Revisit the curriculum systematically before attempting again |

### Weak Area Analysis

**If you missed Tasks 1, 7:** Review API server flags, audit policy YAML structure, and CIS Benchmark remediation patterns.

**If you missed Tasks 5, 9:** Review RBAC (especially ClusterRoleBinding immutability), ServiceAccount hardening, and CertificateSigningRequest workflows.

**If you missed Task 6:** Practice AppArmor profile syntax, Seccomp JSON structure, and the pod spec fields for all three (appArmorProfile, seccompProfile, sysctls). This is a high-value combined skill.

**If you missed Tasks 2, 10, 11, 16:** Review Pod Security Admission labels, EncryptionConfiguration providers, RuntimeClass with scheduling, and ValidatingAdmissionWebhook syntax. These are core microservice vulnerability patterns.

**If you missed Tasks 3, 8, 13:** Practice Kyverno policy syntax, ImagePolicyWebhook configuration, and Trivy scanning workflows. Supply chain security is 20% of the exam.

**If you missed Tasks 4, 12, 14:** Practice Falco rule syntax, incident response procedures, and audit/monitoring setup. These tasks require both security knowledge and quick diagnosis skills.

### Time Management Tips for This Difficulty Level

- **Tasks 15 (Easy, 4 pts):** Complete in under 5 minutes — these are free points
- **Tasks 5, 7, 9, 11, 12, 13 (Medium):** Aim for 7–8 minutes each — ~45 minutes total
- **Tasks 1, 2, 3, 4, 6, 8, 10, 14, 16 (Hard):** Allocate 8–10 minutes each — ~75 minutes total
- **Buffer:** ~0 minutes — This exam has almost no buffer time, which is intentional

If you're running out of time, prioritize completing partial solutions for maximum partial credit rather than spending all remaining time on one hard task.
